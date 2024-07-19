#%%
import logging

from datetime import datetime, timedelta
import geojson
import json
from rov_db_access.element84.tasks import changeDetectTask

logging.basicConfig(level=logging.INFO, format='%(name)s %(asctime)s - %(levelname)-9s: %(message)s')

polygon = geojson.Polygon([
    [
        [ -70.48523426976115, -33.301676801972178 ],
        [ -70.468600100978577, -33.59908210769234 ],
        [ -70.608802380717407, -33.837257568810188 ],
        [ -70.920098967934123, -33.81554282937828 ],
        [ -70.990200107803545, -33.609967570547532 ],
        [ -70.947426530934067, -33.300683746787314 ],
        [ -70.839304433847346, -33.168506722512973 ],
        [ -70.632565478978208, -33.151597519728206 ],
        [ -70.48523426976115, -33.301676801972178 ]
        ] ] 
    )

date_t1 = datetime(year=2022,month=8, day=5)
date_t2 = datetime(year=2023,month=1, day=1)
window = timedelta(days=30)
alpha = 0.8
max_cloud = 80

runs_inputs = changeDetectTask(date_t1,date_t2,polygon,window,alpha,max_cloud)
len(runs_inputs)
