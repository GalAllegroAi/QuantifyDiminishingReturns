from allegroai_api import Session
from allegroai_api.services import events
import json


class ExperimentResults:
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.latest_scalars = None
        self.plots = None
        self.update_latest_scalars_from_running_task()

    def _latest_statistics(self, ev):
        """
        Get the latest statistics and parameters of the task
        :param ev: event: defines which values to ask from the task
        """
        sess = Session()
        task_params = sess.send(ev)
        return task_params

    def update_latest_scalars_from_running_task(self):
        """
        Update the statistics of the task
        """
        ev = events.GetTaskLatestScalarValuesRequest(task=self.task_id)
        self.latest_scalars = self._latest_statistics(ev)
        ev = events.GetTaskPlotsRequest(task=self.task_id)
        self.plots = self._latest_statistics(ev)

    def get_task_name(self):
        return self.latest_scalars.response_data['name']

    def get_task_status(self):
        return self.latest_scalars.response_data['status']

    def get_task_last_iteration(self):
        return self.latest_scalars.response_data['last_iter']

    def get_metrics_titles(self):
        titles = []
        graphs = self.latest_scalars.response_data['metrics']
        for graph in graphs:
            titles.append(graph['name'])

        return titles

    def get_plots_titles(self):
        titles = []
        graphs = self.plots.response_data['plots']
        for graph in graphs:
            titles.append(graph['metric'])

        return titles

    def get_metric_last_values(self, metric_title=None) -> dict:
        metric_titles = self.get_metrics_titles()
        if (metric_title is None) or (metric_title not in metric_titles):
            raise ValueError('There is no such graph in this task.'
                             'Use TaskResults.get_metrics_titles() to get list of available metric titles')

        data = {}
        for graph in self.latest_scalars.response_data['metrics']:
            if graph['name'] == metric_title:
                graph_data = graph['variants']
                for variant in graph_data:
                    data[variant['name']] = variant['last_value']

        return data

    def get_plot_data(self, plot_title=None):
        plot_titles = self.get_plots_titles()
        if (plot_title is None) or (plot_title not in plot_titles):
            raise ValueError('There is no such graph in this task.'
                             'Use TaskResults.get_metrics_titles() to get list of available metric titles')

        data = {}
        for graph in self.plots.response_data['plots']:
            if graph['metric'] == plot_title:
                graph_data = json.loads(graph['plot_str'].replace("'", "\""))['data']  # json acceptable string
                for variant in graph_data:
                    data[variant['name']] = {}
                    data[variant['name']]['x'] = variant['x']
                    data[variant['name']]['y'] = variant['y']

        return data


def main():
    id = '1bbfcd5652cd4558a007a1b54a4cb67a'
    task_stat = ExperimentResults(task_id=id)

    print('\nInformation on task id {}'.format(id))
    print("Task's name: {}".format(task_stat.get_task_name()))
    print("Task's status: {}".format(task_stat.get_task_status()))
    print("Task's laste iteration number: {}".format(task_stat.get_task_last_iteration()))

    print("\nTask's available metrics:")
    for title in task_stat.get_metrics_titles():
        print(title)

    print("\nTask's available plots:")
    for title in task_stat.get_plots_titles():
        print(title)

    print('\nRetrieving data from metric "Average Precision | IOU=0.50":')
    metric_data = task_stat.get_metric_last_values(metric_title='Average Precision | IOU=0.50')
    for key, value in metric_data.items():
        print('{} = {}'.format(key, value))

    print('\nRetrieving data from plot "Precision-Recall @IOU:0.3":')
    metric_data = task_stat.get_plot_data(plot_title='Precision-Recall @IOU:0.3')
    for key, value in metric_data.items():
        print('\n{}:'.format(key))
        print('x values = {}'.format(value['x']))
        print('y values = {}'.format(value['y']))


if __name__ == "__main__":
    main()
