# main.py
from model.worktime_model import WorkTimeModel
from view.worktime_view import WorkTimeView
from controller.worktime_controller import WorkTimeController

model = WorkTimeModel()
view = WorkTimeView()
controller = WorkTimeController(model, view)

view.mainloop()