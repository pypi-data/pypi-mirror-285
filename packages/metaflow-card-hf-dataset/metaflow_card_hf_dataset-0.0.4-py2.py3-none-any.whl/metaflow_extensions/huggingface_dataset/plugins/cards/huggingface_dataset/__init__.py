from metaflow.cards import MetaflowCard
from metaflow.exception import MetaflowException
import datetime

note = f"""This dataset was loaded using the HuggingFace Datasets library at {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.
This card uses HuggingFace's dataset viewer, which let's you view the <b>latest</b> version on HuggingFace, not necessarily the version used in this run.
"""


class HuggingfaceDatasetCard(MetaflowCard):

    type = "huggingface_dataset"

    RUNTIME_UPDATABLE = True
    RELOAD_POLICY = "never"

    def __init__(self, options={"id": None, "artifact_id": None, "vh": 550}, **kwargs):
        if not options.get("id") and not options.get("artifact_id"):
            raise MetaflowException(
                "Dataset ID or Metaflow FlowSpec artifact_id is required for Huggingface Dataset card."
            )
        self.dataset_id = options.get("id", "")
        self.artifact_id = options.get("artifact_id", "")
        self.vh = options.get("vh", 550)

    def render_runtime(self, task, data):
        return self.render(task, runtime=True)

    def render(self, task):
        if not self.dataset_id:
            self.dataset_id = getattr(task.data, self.artifact_id)
        dataset_viewer_url = (
            f"https://huggingface.co/datasets/{self.dataset_id}/embed/viewer"
        )
        return f'<html><body><p>{note}</p><iframe src="{dataset_viewer_url}" width="100%" height="{self.vh}vh"></iframe></body></html>'


CARDS = [HuggingfaceDatasetCard]
