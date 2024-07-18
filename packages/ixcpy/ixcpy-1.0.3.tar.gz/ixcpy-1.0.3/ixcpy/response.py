import json



class Response:


    def __init__(self, payload: str):

        self._total: int = 0
        self._records: list = []

        if payload is not None and not payload.__contains__('</div>') and len(payload) > 0:
            dataset = json.loads(payload)
            if 'total' in dataset and 'registros' in dataset:
                self._total: int = int(dataset['total'])
                self._records: list = dataset['registros']


    def total(self) -> int:
        return self._total
    

    def records(self) -> list:
        return self._records
