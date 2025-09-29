from typing import Any

def validate_price(value: Any) -> Any:
    if value is None:
        return value
    try:        
        v = float(value) # chấp nhận int/float
    except Exception:
        raise ValueError("Giá có định dạng không hợp lệ")    
    if v < 0:
        raise ValueError('Giá không được âm')
    return v

def validate_stock_quantity(value: Any) -> Any:
    if value is None:
        return value
    if not isinstance(value, int):
        raise ValueError("Số lượng tồn kho không hợp lệ")
    if value < 0:
        raise ValueError('Số lượng tồn kho không được âm')
    return value
