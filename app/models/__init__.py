# app/models/__init__.py
# File này tổng hợp import tất cả các model từ các thư mục con khác trong app/
# Mục đích: Cho phép import một lần từ 'app.models' để load hết metadata cho Alembic

from app.users.models import *  
from app.patients.models import *  
from app.medications.models import * 
from app.services.models import *
from app.appointments.models import *
from app.medical_records.models import *
from app.prescriptions.models import *
from app.invoices.models import *
from app.service_indications.models import *

# Nếu có thêm model mới sau này, chỉ cần thêm dòng import tương ứng ở đây