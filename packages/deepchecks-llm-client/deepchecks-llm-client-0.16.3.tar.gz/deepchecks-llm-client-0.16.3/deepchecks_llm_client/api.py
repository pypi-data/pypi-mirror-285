import logging
import typing as t
from copy import copy

import deepchecks_llm_client
import httpx
import packaging.version
from deepchecks_llm_client.data_types import (
    AnnotationType,
    Application,
    ApplicationType,
    ApplicationVersion,
    ApplicationVersionSchema,
    EnvType,
    InteractionCompleteEvents,
    LogInteractionType,
    PropertyColumnType,
    Step,
)
from deepchecks_llm_client.utils import maybe_raise
from httpx import URL

__all__ = ["API"]


logger = logging.getLogger(__name__)

TAPI = t.TypeVar("TAPI", bound="API")  # pylint: disable=invalid-name
MAX_TOPIC_LENGTH = 40


def _check_topic(topic: t.Union[str, None]):
    """Check topic length and log warning that topic must not be more than 40 characters long."""
    if topic and len(topic) > MAX_TOPIC_LENGTH:
        logger.warning(f"Topic {topic} is too long and will be truncated to {MAX_TOPIC_LENGTH} during interaction upload")


class API:
    """DeepchecksLLMClient API class."""

    session: httpx.Client
    original_host: URL

    @classmethod
    def instantiate(cls: t.Type[TAPI],
                    host: str,
                    token: t.Optional[str] = None,
                    validate_connection: bool = False) -> TAPI:
        headers = (
            {"Authorization": f"Basic {token}", "x-deepchecks-origin": "SDK"}
            if token
            else {"x-deepchecks-origin": "SDK"}
        )
        return cls(
            session=httpx.Client(
                base_url=host,
                headers=headers,
                timeout=60
            ),
            validate_connection=validate_connection
        )

    def __init__(self, session: httpx.Client, validate_connection: bool = False):
        self.session = copy(session)
        self.original_host = self.session.base_url
        self.session.base_url = self.session.base_url.join("/api/v1")

        try:
            backend_version = packaging.version.parse(self.retrieve_backend_version())
            client_version = packaging.version.parse(deepchecks_llm_client.__version__)
        except packaging.version.InvalidVersion as ex:
            raise RuntimeError("Not able to compare backend and client versions, "
                               "backend or client use incorrect or legacy versioning schema.") from ex
        except httpx.ConnectError as ex:
            logger.exception(f"Could not connect to backend {self.original_host}, either the server is down or "
                             f"you are using an incorrect host name")
            if validate_connection:
                raise ex

        else:
            if backend_version.major != client_version.major:
                logger.warning(
                    f"You are using an old client version.\n"
                    f"Client version is {client_version}, Backend version is {backend_version}\n"
                    f"We recommend you to upgrade \"deepchecks-llm-client\" version by running:\n"
                    f">> pip install -U deepchecks-llm-client"
                )

    def retrieve_backend_version(self) -> str:
        payload = maybe_raise(self.session.get("backend-version")).json()
        return payload["version"]

    def get_application(self, app_name: str) -> t.Dict[str, t.Any]:
        payload = maybe_raise(self.session.get("applications", params={"name": [app_name]})).json()
        return payload[0] if len(payload) > 0 else None

    def get_applications(self) -> t.List[Application]:
        applications = maybe_raise(self.session.get("applications")).json()
        return [
            Application(
                id=app["id"],
                name=app["name"],
                kind=app["kind"],
                created_at=app["created_at"],
                updated_at=app["updated_at"],
                in_progress=app["in_progress"],
                description=app["description"],
                log_latest_insert_time_epoch=app["log_latest_insert_time_epoch"],
                n_of_llm_properties=app["n_of_llm_properties"],
                n_of_interactions=app["n_of_interactions"],
                notifications_enabled=app["notifications_enabled"],
                versions=[
                    ApplicationVersion(
                        id=app_version["id"],
                        name=app_version["name"],
                        ai_model=app_version["ai_model"],
                        created_at=app_version["created_at"],
                        updated_at=app_version["updated_at"],
                        description=app_version["description"],
                        custom=app_version["custom"]
                    ) for app_version in app["versions"]
                ],
            ) for app in applications
        ]

    def get_versions(self, app_name: t.Optional[str] = None) -> t.List[ApplicationVersion]:
        versions = maybe_raise(self.session.get("application-versions", params={"app_name": [app_name] if app_name else []})).json()
        return [
            ApplicationVersion(
                id=app_version["id"],
                name=app_version["name"],
                ai_model=app_version["ai_model"],
                created_at=app_version["created_at"],
                updated_at=app_version["updated_at"],
                description=app_version["description"],
                custom=app_version["custom"]
            ) for app_version in versions
        ]

    def create_application_version(
        self,
        application_id: int,
        version_name: str,
        description: t.Optional[str] = None,
        custom: t.Optional[t.List[t.Dict[str, t.Any]]] = None,
    ):
        return maybe_raise(
            self.session.post(
                "application-versions",
                json={
                    "application_id": application_id,
                    "name": version_name,
                    "custom": custom,
                    "description": description,
                },
            )
        ).json()

    def create_application(
        self,
        app_name: str,
        app_type: ApplicationType,
        versions: t.Optional[t.List[ApplicationVersionSchema]] = None,
        description: t.Optional[str] = None,
    ):
        return maybe_raise(
            self.session.post(
                "applications",
                json={
                    "name": app_name,
                    "kind": app_type,
                    "versions": [version.to_json() for version in versions] if versions else [],
                    "description": description,
                },
            )
        ).json()

    def annotate(self,
                 user_interaction_id: str,
                 version_id: int,
                 annotation: AnnotationType = None,
                 reason: t.Optional[str] = None) \
            -> t.Optional[httpx.Response]:
        # pylint: disable=redefined-builtin
        return maybe_raise(self.session.put("annotations", json={"user_interaction_id": user_interaction_id,
                                                                 "application_version_id": version_id,
                                                                 "value": annotation.value,
                                                                 "reason": reason}))

    def update_interaction(
            self,
            user_interaction_id: str,
            app_version_id: int,
            annotation: AnnotationType = None,
            annotation_reason: t.Optional[str] = None,
            custom_props: t.Union[t.Dict[str, t.Any], None] = None,
    ) -> t.Optional[httpx.Response]:
        return maybe_raise(
            self.session.put(
                f"application_versions/{app_version_id}/interactions/{user_interaction_id}",
                json={"custom_properties": custom_props, "annotation": annotation, "annotation_reason": annotation_reason},
            )
        )

    def delete_interactions(self, user_interaction_ids: t.List[str], app_version_id: int):
        return maybe_raise(
            self.session.request(
                method="DELETE",
                url="interactions",
                params={"application_version_id": app_version_id},
                json=user_interaction_ids,
            )
        )

    def log_batch(self, app_name: str, version_name: str, env_type: EnvType, interactions: t.List[LogInteractionType]):
        for interaction in interactions:
            if interaction.topic is not None:
                _check_topic(interaction.topic)

        return maybe_raise(
            self.session.post(
                "interactions",
                json={
                    "app_name": app_name,
                    "version_name": version_name,
                    "env_type": env_type.value,
                    "interactions": [interaction.to_json() for interaction in interactions],
                },
            ),
            expected=201,
        )

    def log_interaction(
        self,
        app_name: str,
        version_name: str,
        env_type: EnvType,
        input: str,
        output: str,
        full_prompt: str,
        information_retrieval: t.Union[t.List[str], str],
        annotation: AnnotationType,
        user_interaction_id: str,
        started_at: t.Union[str, float],
        finished_at: t.Union[str, float],
        steps: t.List[Step],
        custom_props: t.Dict[str, t.Any],
        annotation_reason: t.Optional[str] = None,
        vuln_type: t.Optional[str] = None,
        vuln_trigger_str: t.Optional[str] = None,
        topic: t.Optional[str] = None,
    ) -> t.Optional[httpx.Response]:
        """The log_interaction method is used to log user interactions.

        Parameters
        ----------
        app_name : str
            Application name
        version_name : str
            Version name
        env_type : EnvType
            Environment
        input : str
            Input data
        output : str
            Output data
        full_prompt : str
            Full prompt data
        information_retrieval : str
            Information retrieval
        annotation : AnnotationType
            Annotation type of the interaction
        user_interaction_id : str
            Unique identifier of the interaction
        started_at : datetime or float
            Timestamp the interaction started at. Datetime format is deprecated, use timestamp instead
        finished_at : datetime or float
            Timestamp the interaction finished at. Datetime format is deprecated, use timestamp instead
        steps : list of Step
            List of steps taken during the interaction
        custom_props : dict
            Additional custom properties
        annotation_reason : str, optional
            Reason for the annotation
        vuln_type : str, optional
            Type of vulnerability (Only used in case of EnvType.PENTEST and must be sent there).
        vuln_trigger_str : str, optional
            Vulnerability trigger string (Only used in case of EnvType.PENTEST and is optional there).
        topic: str, optional
            Topic associated with the interaction. Topic longer than 40 characters will be truncated
        Returns
        -------
        httpx.Response
            The HTTP response from logging the user interaction

        """
        # pylint: disable=redefined-builtin
        interaction = {
            "user_interaction_id": user_interaction_id,
            "input": input,
            "output": output,
            "full_prompt": full_prompt,
            "information_retrieval": information_retrieval \
                if information_retrieval is None or isinstance(information_retrieval, list) \
                else [information_retrieval],
            "annotation": annotation.value if annotation else None,
            "annotation_reason": annotation_reason,
            "steps": Step.as_jsonl(steps),
            "custom_props": custom_props,
            "vuln_type": vuln_type,
            "vuln_trigger_str": vuln_trigger_str,
        }

        if topic is not None:
            _check_topic(topic)
            interaction["topic"] = topic

        if started_at:
            interaction["started_at"] = started_at

        if finished_at:
            interaction["finished_at"] = finished_at

        return maybe_raise(
            self.session.post(
                "interactions",
                json={"env_type": env_type,
                      "app_name": app_name,
                      "version_name": version_name,
                      "interactions": [interaction]}
            ),
            expected=201
        )

    def get_interactions(self, application_version_id: int,
                         limit: int, offset: int,
                         environment: t.Union[EnvType, str],
                         start_time_epoch: t.Union[int, None],
                         end_time_epoch: t.Union[int, None],
                         user_interaction_ids: t.Union[t.List[str], None] = None) -> t.List:
        return maybe_raise(
            self.session.post("get-interactions-by-filter",
                              json={
                                  "application_version_id": application_version_id,
                                  "environment": environment.value if isinstance(environment, EnvType) else environment,
                                  "limit": limit,
                                  "offset": offset,
                                  "start_time_epoch": start_time_epoch,
                                  "end_time_epoch": end_time_epoch,
                                  "user_interaction_ids": user_interaction_ids,
                              }, params={"return_topics": True, "return_input_props": False})
        ).json()

    def get_interactions_csv(
            self,
            application_version_id: int,
            return_topics: bool,
            return_annotation_data: bool,
            return_input_props: bool,
            return_output_props: bool,
            return_custom_props: bool,
            return_llm_props: bool,
            return_similarities: bool,
            environment: t.Union[EnvType, str],
            start_time_epoch: t.Union[int, None],
            end_time_epoch: t.Union[int, None],
            user_interaction_ids: t.Union[t.List[str], None] = None,
    ) -> str:
        return maybe_raise(
            self.session.post(
                "interactions-download-all-by-filter",
                json={
                    "application_version_id": application_version_id,
                    "environment": environment.value if isinstance(environment, EnvType) else environment,
                    "start_time_epoch": start_time_epoch,
                    "end_time_epoch": end_time_epoch,
                    "user_interaction_ids": user_interaction_ids,
                },
                params={"return_topics": return_topics,
                        "return_input_props": return_input_props,
                        "return_output_props": return_output_props,
                        "return_custom_props": return_custom_props,
                        "return_llm_props": return_llm_props,
                        "return_annotation_data": return_annotation_data,
                        "return_similarities_data": return_similarities,
                        }
            )
        ).text

    def get_interaction_by_user_interaction_id(self, version_id: int, user_interaction_id: str):
        return maybe_raise(self.session.get(
            f"application_versions/{version_id}/interactions/{user_interaction_id}"
        )).json()

    def update_application_config(self, application_id: int, file):
        if isinstance(file, str):
            with open(file, "rb") as f:
                data = {"file": ("filename", f)}
        else:
            data = {"file": ("filename", file)}
        maybe_raise(self.session.put(f"applications/{application_id}/config", files=data))

    def get_application_config(self, application_id: int, file_save_path: t.Union[str, None] = None) -> str:
        text = maybe_raise(self.session.get(f"applications/{application_id}/config")).text
        if file_save_path:
            with open(file_save_path, "w", encoding="utf-8") as f:
                f.write(text)
        return text

    def get_pentest_prompts(
            self,
            app_id: int,
            probes: t.Optional[t.List[str]] = None,
    ) -> str:
        if probes:
            return maybe_raise(self.session.get("pentest-prompts", params={"probes": probes, "app_id": app_id})).text
        return maybe_raise(self.session.get("pentest-prompts", params={"app_id": app_id})).text

    def get_custom_properties_definitions(self, application_id: int) -> t.List[dict]:
        return maybe_raise(self.session.get(f"applications/{application_id}/custom-prop-definitions")).json()

    def update_custom_property_definition(self, application_id: int, old_name: str, new_name: str, description: str) -> None:
        return maybe_raise(
            self.session.put(
                f"applications/{application_id}/custom-prop-definitions",
                json=[{"old_name": old_name, "new_name": new_name, "description": description}]
            )
        )

    def create_custom_property_definition(self, application_id: int, name: str, prop_type: PropertyColumnType, description: str = "") -> None:
        return maybe_raise(
            self.session.post(
                f"applications/{application_id}/custom-prop-definitions",
                json=[{"display_name": name, "type": prop_type.value, "description": description}]
            )
        )

    def delete_custom_property_definition(self, application_id: int, name: str):
        return maybe_raise(
            self.session.delete(
                f"applications/{application_id}/custom-prop-definitions",
                params={"prop_names_to_delete": [name]}
            )
        )

    def get_interactions_complete_status(
        self,
        app_version_id: int,
        events_to_check: t.List[InteractionCompleteEvents],
        user_interaction_ids: t.List[str],
    ) -> t.Dict[InteractionCompleteEvents, bool]:
        return maybe_raise(
            self.session.post(
                f"application-versions/{app_version_id}/interactions/complete-status",
                json={"events_to_check": events_to_check, "user_interaction_ids": user_interaction_ids}
            )
        ).json()
