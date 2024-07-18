import honeyhive
import os

def export_dataset(project, dataset_name, api_key):
	if not api_key:
		api_key = os.environ["HH_API_KEY"] 
	s = honeyhive.HoneyHive(
		bearer_auth=api_key
	)
	datapoint_ids = []
	dataset_name = dataset_name
	res = s.datasets.get_datasets(project=project)
    if res.object is not None:
		for dataset in res.object.datasets:
			if dataset.name == dataset_name:
				datapoint_ids = dataset.datapoints
				break
		pass

	datapoints_res = s.datapoints.get_datapoints(project=project, datapoint_ids=datapoint_ids)

	if datapoints_res.object is not None:
		# handle response
		return datapoints_res.object.datapoints
	else:
		return []

__all__ = ['export_dataset']
