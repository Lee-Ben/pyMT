from PyQt5.uic import loadUiType
from PyQt5 import QtWidgets, QtCore, QtGui
from pyMT.GUI_common.classes import FileInputParser
from pyMT.DataGUI.data_plot import DataMain
from pyMT.ModelGUI.model_viewer import ModelWindow
import sys
import os


path = os.path.dirname(os.path.realpath(__file__))
model_viewer_jpg = path + '/model_viewer.jpg'
data_plot_jpg = path + '/data_plot.jpg'
Ui_MainWindow, QMainWindow = loadUiType(os.path.join(path, 'gateway_main.ui'))
Ui_NewProject, QNewProject = loadUiType(os.path.join(path, 'new_project.ui'))


class NewProject(QNewProject, Ui_NewProject):
    def __init__(self):
        super(NewProject, self).__init__()
        self.setupUi(self)
        self.any_datasets = False
        self.datasets = {}
        self.current_dir = path
        self.project_path = path
        self.dp_windows = []
        self.model_windows = []
        # self.dataset_index = 0
        self.file_to_index = {'dataset': 0, 'list': 1, 'data': 2, 'response': 3, 'model': 4}
        self.index_to_file = {0: 'dataset', 1: 'list', 2: 'data', 3: 'response', 4: 'model'}
        # self.datasetTree.setColumnCount(4)
        # self.datasetTree.setHeaderItem(QtWidgets.QTreeWidgetItem(['Dataset', 'List', 'Data', 'Response', 'Model']))
        self.setup_widgets()
        ret = self.open_project()
        if not ret:
            self.init_dataset_table()
        # self.add_dataset()

    @property
    def dataset_index(self):
        return sorted(set(index.row() for index in
                      self.datasetTable.selectedIndexes()))

    @property
    def empty_table(self):
        for row in range(self.datasetTable.rowCount()):
            for col in range(self.datasetTable.columnCount()):
                item = self.datasetTable.item(row, col)
                if item:
                    if item.text():
                        return False
        return True

    # @property
    def dataset_dict(self):
        ds_dict = {}
        for row in range(self.datasetTable.rowCount()):
            ds_name = self.datasetTable.item(row, 0).text()
            ds_dict.update({ds_name: {}})
            for col in range(1, self.datasetTable.columnCount()):
                item = self.datasetTable.item(row, col)
                if item:
                    ds_dict[ds_name].update({self.index_to_file[col]: item.text()})
        return ds_dict

    def active_datasets(self):
        ds_dict = {}
        active_rows = self.dataset_index
        for row in active_rows:
            ds_name = self.datasetTable.item(row, 0).text()
            ds_dict.update({ds_name: {}})
            for col in range(1, self.datasetTable.columnCount()):
                item = self.datasetTable.item(row, col)
                if item:
                    ds_dict[ds_name].update({self.index_to_file[col]: item.text()})
        return ds_dict

    def setup_widgets(self):
        # pass
        self.addDataset.clicked.connect(self.add_dataset)
        self.deleteDataset.clicked.connect(self.delete_dataset)
        # self.datasetTable.itemPressed.connect(self.modify_table_cell)
        self.datasetTable.cellChanged.connect(self.modify_table_cell)
        self.saveProject.clicked.connect(self.save_project)
        self.openProject.clicked.connect(self.open_project)
        # self.datasetTable.itemDoubleClicked.connect(self.modify_table_cell)
        self.browseButton.clicked.connect(self.browse_files)
        self.projectName.setText('')
        self.launchDataPlot.clicked.connect(self.launch_data_plot)
        self.launchDataPlot.setIcon(QtGui.QIcon(data_plot_jpg))
        self.launchDataPlot.setIconSize(QtCore.QSize(128,128))
        self.launchModelViewer.clicked.connect(self.launch_model_viewer)
        self.launchModelViewer.setIcon(QtGui.QIcon(model_viewer_jpg))
        self.launchModelViewer.setIconSize(QtCore.QSize(128,128))
        # self.addDataset.clicked.connect(self.add_dataset)
        # self.addList.clicked.connect(self.add_list)
        # self.addData.clicked.connect(self.add_data)
        # self.addResponse.clicked.connect(self.add_response)
        # self.addModel.clicked.connect(self.add_model)

    def sort_files(self, files):
        ret_dict = {}
        types = ('model', 'dat', 'resp', 'lst', 'reso')

        for file in files:
            name, ext = os.path.splitext(file)
            if ext in ('.rho', '.model'):
                ret_dict.update({'model': file})
            elif ext in ('.dat', '.data'):
                with open(file, 'r') as f:
                    line = f.readline()
                if 'response' in line:
                    ret_dict.update({'response': file})
                else:
                    ret_dict.update({'data': file})
            elif ext in ('.lst', '.list'):
                ret_dict.update({'list': file})
            elif ext in ('.reso', '.resolution'):
                ret_dict.update({'resolution': file})
        return ret_dict

    def init_dataset_table(self, files_dict=None):
        header = ('Dataset', 'List', 'Data', 'Response', 'Model') #, 'Path')
        self.datasetTable.setColumnCount(5)
        for ii, label in enumerate(header):
                self.datasetTable.setHorizontalHeaderItem(ii, QtWidgets.QTableWidgetItem(label))
        if files_dict:
            row = 0
            # print(files_dict)
            self.datasetTable.setRowCount(len(files_dict))
            for dataset_name, startup in files_dict.items():
                try:
                    self.datasetTable.setItem(row, 0, QtWidgets.QTableWidgetItem(dataset_name))
                    self.datasetTable.setItem(row, 1, QtWidgets.QTableWidgetItem(startup.get('list', '')))
                    self.datasetTable.setItem(row, 2, QtWidgets.QTableWidgetItem(startup.get('data', '')))
                    self.datasetTable.setItem(row, 3, QtWidgets.QTableWidgetItem(startup.get('response', '')))
                    self.datasetTable.setItem(row, 4, QtWidgets.QTableWidgetItem(startup.get('model', '')))
                    # print(dataset_name)
                except KeyError:
                    pass
                row += 1
        else:
            self.datasetTable.setRowCount(1)
            self.datasetTable.setItem(0, 0, QtWidgets.QTableWidgetItem('ds1'))
            for col in range(1, 6):
                self.datasetTable.setItem(0, col, QtWidgets.QTableWidgetItem(''))

    def update_dataset_table(self, files):
        sorted_files = self.sort_files(files=files)
        # print(files)
        for key, value in sorted_files.items():
            self.datasetTable.setItem(self.dataset_index[0], self.file_to_index[key], QtWidgets.QTableWidgetItem(value))

    def add_dataset(self):
        self.datasetTable.setRowCount(self.datasetTable.rowCount() + 1)
        self.datasetTable.setItem(self.datasetTable.rowCount() - 1, 0,
                                  QtWidgets.QTableWidgetItem('ds{}'.format(self.datasetTable.rowCount())))
        # self.datasetTabel.item()

    def delete_dataset(self):
        self.datasetTable.removeRow(self.dataset_index)

    # def modify_table_cell(self, item):
    def modify_table_cell(self, row, col):
        item = self.datasetTable.item(row, col)
        if item:
            if item.column() == 0:
                for row in range(self.datasetTable.rowCount()):
                    if row != item.row():
                        if item.text() == self.datasetTable.item(row, 0).text():
                            text = ''
                            while True:
                                if text:
                                    item.setText(text)
                                    break
                                else:
                                    text, ok = QtWidgets.QInputDialog.getText(self, '', 'Data sets must have unique names. Enter a new name: ')
                                

    def save_project(self):
        # if not project_name:
        #     QtWidgets.QMessageBox.warning(self, '...', 'You have to name the project first!')
        #     return
        all_datasets = {}
        for row in range(self.datasetTable.rowCount()):
            # dataset, lst, data, response, model = '', '', '', '', ''
            dataset = []
            for col in range(self.datasetTable.columnCount()):
                item = self.datasetTable.item(row, col)
                if item:
                    dataset.append(self.datasetTable.item(row, col).text())
                else:
                    dataset.append('')
            if not dataset[0]:
                QtWidgets.QMessageBox.warning(self, '...', 'Dataset in row {} needs a name!'.format(row + 1))
                return
            if any(dataset):
                all_datasets.update({dataset[0]: {'list': dataset[1], 'data': dataset[2], 'resp': dataset[3], 'model': dataset[4]}})
        self.write_project(all_datasets)

    def open_project(self):
        files_dict = None
        
        if self.empty_table:
            # continue
            pass
            # self.init_dataset_table(files_dict)
            # return
        else:
            retval = QtWidgets.QMessageBox.question(self, '', 'Do you want to save the current project first?',
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)
            if retval == QtWidgets.QMessageBox.Yes:
                self.save_project()
                # self.init_dataset_table(files_dict)
            elif retval == QtWidgets.QMessageBox.No:
                # self.init_dataset_table(files_dict)
                # continue
                pass
            elif retval == QtWidgets.QMessageBox.Cancel:
                return False
        project_file = QtWidgets.QFileDialog.getSaveFileName(self, 'Open Project', '',
                                                             'pyMT Project Files (*.pymt);; All Files (*)',
                                                             options=QtWidgets.QFileDialog.DontConfirmOverwrite)[0]
        # print(project_file)
        if project_file:
            if os.path.exists(project_file):
                files_dict = FileInputParser.read_pystart(project_file)
        self.projectName.setText(os.path.basename(project_file))
        self.datasetTable.cellChanged.disconnect()
        self.init_dataset_table(files_dict)
        self.datasetTable.cellChanged.connect(self.modify_table_cell)
        self.project_path = os.path.dirname(project_file)
        return True

    def write_project(self, all_datasets):
        # Create / Modify should be one button, and if you choose a non-existant file it starts as we have so far, but if you choose an existing file
        # It loads it. That way project naming / loading happens immediately

        project_file = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Project', '', 'pyMT Project Files (*.pymt);; All Files (*)')[0]
        # print(all_datasets)
        if project_file:
            with open(project_file, 'w') as f:
                for name, dataset in all_datasets.items():
                    f.write('% {}\n'.format(name))
                    for file_type in ('list', 'data', 'resp', 'model'):
                        try:
                            file = dataset[file_type]
                            if file:
                                f.write('{} {}\n'.format(file_type, file))
                        except KeyError:
                            pass
                self.projectName.setText(os.path.basename(project_file))
            # self.close()
            # if os.path.exists(project_file):
            #     pass
                
    def browse_files(self):
        if len(self.dataset_index) == 1:
            fnames = QtWidgets.QFileDialog.getOpenFileNames(self, 'Browse Files',
                                                           self.current_dir,
                                                           'ModEM Files (*.rho *.model *.dat *.lst);; All Files (*)')[0]
            if fnames:
                self.current_dir = os.path.abspath(fnames[0])
                # print(fnames)
                # if len(fnames) == 1:
                    # fnames = fnames[0]
                self.update_dataset_table(fnames)
        else:
            QtWidgets.QMessageBox.warning(self, '', 'You must select (highlight) a single dataset to add to!')

    def launch_data_plot(self):
        if len(self.dataset_index) < 0:
            QtWidgets.QMessageBox.warning(self, '', 'Select (highlight) the desired dataset(s) first.')
            return
        active_ds = self.active_datasets()
        self.dp_windows.append(DataMain(dataset_dict=active_ds))
        self.dp_windows[-1].show()
        # print({key: ds_dict[key] for key in self.dataset_index})

    def launch_model_viewer(self):
        if len(self.dataset_index) < 0:
            QtWidgets.QMessageBox.warning(self, '', 'Select (highlight) the desired dataset(s) first.')
            return
        elif len(self.dataset_index) > 1:
            QtWidgets.QMessageBox.warning(self, '', 'Model Viewer can only load one data set at a time (for now)...')
            return
        active_ds = self.active_datasets()
        # try:
        ds = list(active_ds.values())[0]
        model = ds.get('model', None)
        if model:
            self.model_windows.append(ModelWindow(files=ds))
            self.model_windows[-1].show()
        else:
            QtWidgets.QMessageBox.warning(self, '', 'A model must be available in the selected data set to use Model Viewer!')


class GatewayMain(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(GatewayMain, self).__init__()
        self.setupUi(self)
        self.setup_widgets()

    def setup_widgets(self):
        self.newProject.clicked.connect(self.new_project)
        self.loadProject.clicked.connect(self.load_project)
        self.modifyProject.clicked.connect(self.modify_project)

    def new_project(self):
        self.new_project_window = NewProject(parent=self)
        self.new_project_window.show()

    def load_project(self):
        pass

    def modify_project(self):
        pass


# If this is run directly, launch the GUI
def main():
    app = QtWidgets.QApplication(sys.argv)  # Starts GUI event loop
    mainGUI = NewProject()  # Instantiate a GUI window
    mainGUI.show()  # Show it.
    ret = app.exec_()
    sys.exit(ret)  # Properly close the loop when the window is closed.
    # mainGUI.disconnect_mpl_events()
    print('Exiting')


if __name__ == '__main__':
    main()
    # print('Done.')