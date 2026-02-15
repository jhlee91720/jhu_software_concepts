"""Test doubles for DB connection/cursor behavior."""


def sample_row(url_suffix="1", status="Accepted", citizenship="International"):
    return {
        "program": "Johns Hopkins University Computer Science",
        "comments": "sample",
        "date_added": "2026-01-01",
        "url": f"https://example.com/{url_suffix}",
        "applicant_status": status,
        "semester_year_start": "Fall 2026",
        "citizenship": citizenship,
        "gpa": "3.9",
        "gre": "330",
        "gre_v": "162",
        "gre_aw": "4.5",
        "masters_or_phd": "Masters",
        "llm-generated-program": "Computer Science",
        "llm-generated-university": "Johns Hopkins University",
    }


class FakeConn:
    def __init__(self):
        self.rows = []
        self._url_index = set()
        self.commits = 0

    def cursor(self):
        return FakeCursor(self)

    def commit(self):
        self.commits += 1

    def close(self):
        return None


class FakeCursor:
    def __init__(self, conn):
        self.conn = conn
        self._last_one = None
        self.rowcount = 0

    def execute(self, sql, params=None):
        statement = " ".join(sql.split()).lower()
        params = params or ()

        if statement.startswith("create table"):
            self.rowcount = 0
            return

        if statement.startswith("insert into applicants"):
            url = params[3]
            if url in self.conn._url_index:
                self.rowcount = 0
                return

            row = {
                "program": params[0],
                "comments": params[1],
                "date_added": params[2],
                "url": params[3],
                "status": params[4],
                "term": params[5],
                "us_or_international": params[6],
                "gpa": params[7],
                "gre": params[8],
                "gre_v": params[9],
                "gre_aw": params[10],
                "degree": params[11],
                "llm_generated_program": params[12],
                "llm_generated_university": params[13],
            }
            self.conn.rows.append(row)
            self.conn._url_index.add(url)
            self.rowcount = 1
            return

        if statement.startswith("select count(*) from applicants") and "where" not in statement:
            self._last_one = (len(self.conn.rows),)
            return

        if "where us_or_international = %s" in statement:
            target = params[0]
            count = sum(1 for row in self.conn.rows if row.get("us_or_international") == target)
            self._last_one = (count,)
            return

        if "where lower(status) like" in statement:
            count = sum(1 for row in self.conn.rows if "accept" in str(row.get("status", "")).lower())
            self._last_one = (count,)
            return

        raise AssertionError(f"Unsupported SQL in fake cursor: {sql}")

    def fetchone(self):
        return self._last_one

    def close(self):
        return None
