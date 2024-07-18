from metaflow.decorators import StepDecorator
from metaflow.exception import MetaflowException
from collections import defaultdict
import json
import uuid

CARD_TYPE = "huggingface_dataset"
VERTICAL_HEIGHT_DEFAULT = 550


class CardDecoratorInjector:
    """
    Mixin Useful for injecting @card decorators from other first class Metaflow decorators.
    """

    _first_time_init = defaultdict(dict)

    @classmethod
    def _get_first_time_init_cached_value(cls, step_name, card_id):
        return cls._first_time_init.get(step_name, {}).get(card_id, None)

    @classmethod
    def _set_first_time_init_cached_value(cls, step_name, card_id, value):
        cls._first_time_init[step_name][card_id] = value

    def _card_deco_already_attached(self, step, card_id):
        for decorator in step.decorators:
            if decorator.name == "card":
                if decorator.attributes["id"] and card_id in decorator.attributes["id"]:
                    return True
        return False

    def _get_step(self, flow, step_name):
        for step in flow:
            if step.name == step_name:
                return step
        return None

    def _first_time_init_check(self, step_dag_node, card_id):
        """ """
        return not self._card_deco_already_attached(step_dag_node, card_id)

    def attach_card_decorator(self, flow, step_name, card_id, card_type, options):
        """
        This method is called `step_init` in your StepDecorator code since
        this class is used as a Mixin
        """
        from metaflow import decorators as _decorators

        if not all([card_id, card_type]):
            raise MetaflowException(
                "`INJECTED_CARD_ID` and `INJECTED_CARD_TYPE` must be set in the `CardDecoratorInjector` Mixin"
            )

        step_dag_node = self._get_step(flow, step_name)
        if (
            self._get_first_time_init_cached_value(step_name, card_id) is None
        ):  # First check class level setting.
            if self._first_time_init_check(step_dag_node, card_id):
                self._set_first_time_init_cached_value(step_name, card_id, True)
                _decorators._attach_decorators_to_step(
                    step_dag_node,
                    [
                        "card:type=%s,id=%s,options=%s"
                        % (CARD_TYPE, card_id, json.dumps(options))
                    ],
                )
            else:
                self._set_first_time_init_cached_value(step_name, card_id, False)


class HuggingfaceDatasetDecorator(StepDecorator, CardDecoratorInjector):

    name = CARD_TYPE
    defaults = {"id": None, "artifact_id": None, "vh": 550}
    allow_multiple = True

    def step_init(
        self, flow, graph, step_name, decorators, environment, flow_datastore, logger
    ):

        if not self.attributes.get("id") and not self.attributes.get("artifact_id"):
            raise MetaflowException(
                "Dataset ID or Metaflow FlowSpec artifact_id is required for Huggingface Dataset card."
            )

        if (
            self.attributes.get("id") is not None
            and self.attributes.get("artifact_id") is not None
        ):
            raise MetaflowException(
                "Both Dataset ID and Metaflow FlowSpec artifact_id cannot be set at the same time."
            )

        if self.attributes.get("id"):
            _id = self.attributes.get("id").replace("/", "_").replace("-", "_")
        else:
            _id = self.attributes.get("artifact_id")

        self.attach_card_decorator(
            flow,
            step_name,
            _id,
            CARD_TYPE,
            options={
                "id": self.attributes.get("id"),
                "artifact_id": self.attributes.get("artifact_id"),
                "vh": self.attributes.get("vh", 550),
            },
        )
