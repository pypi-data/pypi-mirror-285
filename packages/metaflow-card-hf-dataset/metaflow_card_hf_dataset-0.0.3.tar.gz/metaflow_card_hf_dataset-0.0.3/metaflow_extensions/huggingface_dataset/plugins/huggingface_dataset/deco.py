from metaflow.decorators import StepDecorator

class huggingface_dataset_deco:

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __call__(self, step_func):

        from metaflow import _huggingface_dataset, card, current

        _card = card(
            type="huggingface_dataset",
            id=self.kwargs.get("id").replace("/", "_").replace("-", "_"),
            options={
                "id": self.kwargs.get("id"),
                "vh": self.kwargs.get("vh", 550)
            }
        )

        return _card(_huggingface_dataset(**self.kwargs)(step_func))


class HuggingfaceDatasetDecorator(StepDecorator):

    name = "_huggingface_dataset"
    defaults = {"id": None}