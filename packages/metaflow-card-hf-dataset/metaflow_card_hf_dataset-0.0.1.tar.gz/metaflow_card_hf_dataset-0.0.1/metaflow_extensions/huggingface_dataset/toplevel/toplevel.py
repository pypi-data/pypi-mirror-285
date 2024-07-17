__mf_extensions__ = "huggingface_dataset"

from ..plugins.huggingface_dataset.deco import huggingface_dataset_deco as huggingface_dataset
import pkg_resources

try:
    __version__ = pkg_resources.get_distribution("metaflow-card-hfdataset").version
except:
    # this happens on remote environments since the job package
    # does not have a version
    __version__ = None