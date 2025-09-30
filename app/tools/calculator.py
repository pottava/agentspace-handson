def add(a: float, b: float) -> dict:
    """2 つの数値を足し算します。"""
    return {"status": "success", "result": f"{a + b}"}


def subtract(a: float, b: float) -> dict:
    """2 つの数値を引き算します。"""
    return {"status": "success", "result": f"{a - b}"}


def multiply(a: float, b: float) -> dict:
    """2 つの数値を掛け算します。"""
    return {"status": "success", "result": f"{a * b}"}


def divide(a: float, b: float) -> dict:
    """数値 a を数値 b で割り算します。ゼロ除算の場合はエラーを返します。"""
    if not a:
        return {"status": "success", "result": "0"}
    if b == 0:
        return {"status": "エラー: ゼロでは割り算できません"}
    return {"status": "success", "result": f"{a / b}"}
