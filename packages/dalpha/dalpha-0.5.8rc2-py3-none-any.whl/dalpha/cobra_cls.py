class Cobra:
    def __init__(self, label = None):
        pass
    
    def __enter__(self):
        return self
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __call__(self, func_or_cls):
        # 이 데코레이터는 함수나 클래스를 그대로 반환합니다.
        return func_or_cls
    
    @classmethod
    def block(cls, label = None):
        # 새 인스턴스를 생성하고, 이 인스턴스는 __call__을 통해 함수나 클래스를 그대로 반환합니다.
        return cls(label)
