# Import basic libs
import json

from qgis.core import (
    NULL,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
)

# Import PyQt libs
from qgis.PyQt.QtCore import QObject, QUrl, pyqtSignal
from qgis.PyQt.QtNetwork import QNetworkReply, QNetworkRequest

from inaturalist_extractor.__about__ import (
    __per_page_limit__,
    __plugin_name__,
    __service_crs__,
    __version__,
)


class ImportData(QObject):
    finished_dl = pyqtSignal()
    """
    Class used to import data to QGIS with the iNaturalist API.
    Data is extracted 20 obs at a time.
    """

    def __init__(
        self,
        network_manager=None,
        project=None,
        layer=None,
        extent=None,
        dlg=None,
        url=None,
    ):
        super().__init__()
        # Count the download
        self._pending_downloads = 0
        # Count the pages of observations
        self._pending_pages = 1
        # Count the observations
        self._pending_count = 0
        self.network_manager = network_manager
        self.project = project
        self.layer = layer
        self.extent = extent
        self.dlg = dlg
        self.url = url

        self.new_features = []

        # Max observations and obs py page limit variables
        self.limit = None
        self.max_obs = None
        self.total_pages = 0

    @property
    def pending_downloads(self):
        return self._pending_downloads

    @property
    def pending_pages(self):
        return self._pending_pages

    @property
    def pending_count(self):
        return self._pending_count

    def download(self, max_obs):
        if not self.max_obs:
            self.max_obs = max_obs
            # Adapt per_page results based on api recommandations
            if self.max_obs > int(__per_page_limit__):
                self.limit = int(__per_page_limit__)
            else:
                self.limit = self.max_obs
            # Laucnch The progress bar
            if float(self.max_obs / self.limit) <= 1:
                self.total_pages = int(self.max_obs / self.limit)
            else:
                self.total_pages = int(self.max_obs / self.limit) + 1
            self.dlg.thread.set_max(self.total_pages)
            self.dlg.thread.add_one(0)
            self.dlg.select_progress_bar_label.setText(
                self.tr("Downloaded data : " + str(0) + "/" + str(self.max_obs))
            )
        # Change the url after every download page with the pending variables.
        if self.dlg.verifiable_checkbox.isChecked():
            verifiable = "verifiable=true&"
        else:
            verifiable = ""
        url = "{url}?verifiable={verifiable}&order_by=id&order=desc&spam=false&page={page}&swlng={xmin}&swlat={ymin}&nelng={xmax}&nelat={ymax}&locale=fr&per_page={limit}".format(  # noqa: E501
            url=self.url,
            page=self.pending_pages,
            xmin=self.extent.xMinimum(),
            ymin=self.extent.yMinimum(),
            xmax=self.extent.xMaximum(),
            ymax=self.extent.yMaximum(),
            limit=self.limit,
            verifiable=verifiable,
        )

        url = QUrl(url)
        request = QNetworkRequest(url)
        request.setRawHeader(
            b"User-Agent", bytes(__plugin_name__ + "/" + __version__, encoding="utf-8")
        )
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
        # GET Request
        reply = self.network_manager.get(request)
        # Launche a function when the downloading is finished
        reply.finished.connect(lambda: self.handle_finished(reply))
        self._pending_downloads += 1

    def handle_finished(self, reply):
        self._pending_downloads -= 1
        if reply.error() != QNetworkReply.NoError:
            print(f"code: {reply.error()} message: {reply.errorString()}")
            if reply.error() == 403:
                print("Service down")
        else:
            data_request = reply.readAll().data().decode()
            if self.pending_downloads == 0:
                res = json.loads(data_request)
                self.specific_api_operation(res)

                # While the actual page number is lower than the total number, update
                # progress bar and download a new page
                if self.pending_pages < self.total_pages:
                    self.dlg.select_progress_bar_label.setText(
                        self.tr(
                            "Downloaded data : "
                            + str(self.pending_count)
                            + "/"
                            + str(self.max_obs)
                        )
                    )
                    self.dlg.thread.add_one(self.pending_pages)
                    self._pending_pages += 1
                    self._pending_count += self.limit
                    self.download(None)
                else:
                    self.dlg.select_progress_bar_label.setText(
                        self.tr(
                            "Downloaded data : "
                            + str(self.max_obs)
                            + "/"
                            + str(self.max_obs)
                        )
                    )
                    self.dlg.thread.add_one(self.pending_pages)
                    # Add the new feature to the temporary layer
                    self.layer.startEditing()
                    self.layer.dataProvider().addFeatures(self.new_features)
                    self.layer.updateExtents()
                    self.layer.commitChanges()
                    self.layer.triggerRepaint()
                    # Emit signal when finished
                    self.finished_dl.emit()

    def specific_api_operation(self, request_result):
        # add a feature in the layer for every observation
        for obs in request_result["results"]:
            # Create feature
            new_feature = QgsFeature(self.layer.fields())

            # Add a geometry
            new_geom = QgsGeometry.fromPointXY(
                QgsPointXY(
                    obs["geojson"]["coordinates"][0],
                    obs["geojson"]["coordinates"][1],
                )
            )
            # Function used to reproject a geometry
            new_geom.transform(
                QgsCoordinateTransform(
                    QgsCoordinateReferenceSystem(int(__service_crs__)),
                    self.dlg.crs_selector.crs(),
                    self.project,
                )
            )
            new_feature.setGeometry(new_geom)

            # Complete feature field one by one
            field_index = 0
            new_feature.setAttribute(field_index, obs["id"])
            field_index += 1
            if "iconic_taxon_name" in list(obs["taxon"].keys()):
                new_feature.setAttribute(field_index, obs["taxon"]["iconic_taxon_name"])
            else:
                new_feature.setAttribute(field_index, NULL)
            field_index += 1

            if "min_species_taxon_id" in list(obs["taxon"].keys()):
                new_feature.setAttribute(
                    field_index, obs["taxon"]["min_species_taxon_id"]
                )
            else:
                new_feature.setAttribute(field_index, NULL)
            field_index += 1

            if "rank" in list(obs["taxon"].keys()):
                new_feature.setAttribute(field_index, obs["taxon"]["rank"])
            else:
                new_feature.setAttribute(field_index, NULL)
            field_index += 1

            if "name" in list(obs["taxon"].keys()):
                new_feature.setAttribute(field_index, obs["taxon"]["name"])
            else:
                new_feature.setAttribute(field_index, NULL)

            field_index += 1

            new_feature.setAttribute(field_index, obs["user"]["login"])
            field_index += 1

            new_feature.setAttribute(field_index, obs["user"]["name"])
            field_index += 1

            if obs["time_observed_at"] != "None":
                new_feature.setAttribute(field_index, obs["time_observed_at"])
            elif obs["observed_on_details"]["date"] != "None":
                new_feature.setAttribute(
                    field_index, obs["observed_on_details"]["date"]
                )
            else:
                new_feature.setAttribute(field_index, NULL)
            field_index += 1

            new_feature.setAttribute(field_index, obs["description"])
            field_index += 1

            new_feature.setAttribute(field_index, obs["quality_grade"])
            field_index += 1

            new_feature.setAttribute(field_index, obs["geoprivacy"])
            field_index += 1

            new_feature.setAttribute(field_index, obs["positional_accuracy"])
            field_index += 1

            new_feature.setAttribute(field_index, obs["uri"])
            field_index += 1

            new_feature.setAttribute(
                field_index,
                "https://www.inaturalist.org/taxa/{taxon_id}".format(
                    taxon_id=obs["taxon"]["min_species_taxon_id"]
                ),
            )
            field_index += 1
            if len(obs["observation_photos"]) > 0:
                new_feature.setAttribute(
                    field_index,
                    obs["observation_photos"][0]["photo"]["url"].replace(
                        "square.jpg", "large.jpg"
                    ),
                )
                field_index += 1

                if len(obs["observation_photos"]) > 1:
                    new_feature.setAttribute(
                        field_index,
                        obs["observation_photos"][1]["photo"]["url"].replace(
                            "square.jpg", "large.jpg"
                        ),
                    )
                    field_index += 1

                    if len(obs["observation_photos"]) > 2:
                        new_feature.setAttribute(
                            field_index,
                            obs["observation_photos"][2]["photo"]["url"].replace(
                                "square.jpg", "large.jpg"
                            ),
                        )

            # Add the feature to the list.
            self.new_features.append(new_feature)
