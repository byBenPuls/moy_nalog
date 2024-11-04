from datetime import datetime, timezone

from moy_nalog.methods import AddIncomeMethod



class TestDateToLocalISO:
    instance = AddIncomeMethod("test")
    method = instance._date_to_local_iso

    def test_current_date(self):
        assert self.method(datetime.now())
    
    def test_special_date(self):
        # check on ISO 6801
        # https://ru.wikipedia.org/wiki/ISO_8601

        assert self.method(datetime(2024, 10, 3)) == "2024-10-03T00:00:00+00:00"
        assert self.method(datetime(2022, 3, 10)) == "2022-03-10T00:00:00+00:00"

    def test_date_unique(self):
        for _ in range(100):
            date = datetime.now().replace(microsecond=0).replace(tzinfo=timezone.utc)
            string_date = self.method(date)
            assert date == datetime.fromisoformat(string_date[:-6])
        for _ in range(100):
            date = datetime.now().replace(microsecond=0).replace()
            string_date = self.method()
            assert date == datetime.fromisoformat(string_date[:-6])
