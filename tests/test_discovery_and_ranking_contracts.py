from modules.discovery.job import Job
from modules.discovery.job_crawler import JobCrawler
from modules.discovery.providers.lever_provider import LeverProvider
from modules.ranking.job_ranker import JobRanker


PROFILE = {"skills": ["SQL", "Power BI", "Excel", "Python"]}


class FakeLocator:
    def __init__(self, links=None, text=""):
        self.links = links or []
        self.text = text

    def count(self):
        return len(self.links)

    def nth(self, index):
        return self.links[index]

    def inner_text(self):
        return self.text


class FakeLink:
    def __init__(self, url, text):
        self.url = url
        self.text = text

    def get_attribute(self, name):
        assert name == "href"
        return self.url

    def inner_text(self):
        return self.text


class FakeJobPage:
    def locator(self, selector):
        assert selector == "body"
        return FakeLocator(text="Data Analyst\nRemote\nUse SQL and Power BI")

    def title(self):
        return "Example Company - Data Analyst"


class FakeBrowser:
    def __init__(self):
        self.closed = False

    def start(self):
        pass

    def open(self, url):
        if url.endswith("gohighlevel"):
            self.page = type("CareerPage", (), {
                "locator": lambda _, selector: FakeLocator([
                    FakeLink("https://jobs.lever.co/gohighlevel/broken", "Broken"),
                    FakeLink("https://jobs.lever.co/gohighlevel/data", "Data Analyst"),
                ])
            })()
            return self.page
        if url.endswith("broken"):
            raise TimeoutError("transient navigation timeout")
        return FakeJobPage()

    def close(self):
        self.closed = True


class FakeParser:
    def parse(self, page):
        return {"skills": ["SQL", "Power BI"], "page_text": "parsed"}


def test_lever_provider_skips_one_failed_job_and_keeps_enriching(monkeypatch):
    browser = FakeBrowser()
    monkeypatch.setattr(
        "modules.discovery.providers.lever_provider.BrowserManager",
        lambda: browser,
    )
    provider = LeverProvider(PROFILE, "https://jobs.lever.co/gohighlevel")
    provider.parser = FakeParser()

    jobs = provider.discover()

    assert [job.title for job in jobs] == ["Data Analyst"]
    assert all(isinstance(job, Job) for job in jobs)
    assert browser.closed is True


def test_ranker_keeps_target_job_above_unrelated_jobs():
    jobs = [
        Job("Software Engineer", "Example", "Remote", "https://example.test/1", "", "test", ["SQL", "Power BI"]),
        Job("Reporting Analyst", "Example", "Remote", "https://example.test/2", "", "test", ["SQL", "Power BI"]),
        Job("Data Analyst", "Example", "Remote", "https://example.test/3", "", "test", ["SQL", "Power BI"]),
    ]

    ranked = JobRanker(PROFILE).rank(jobs)

    assert [entry["job"].title for entry in ranked] == [
        "Data Analyst", "Reporting Analyst", "Software Engineer"
    ]
    assert ranked[-1]["score"] == 0


def test_greenhouse_crawler_returns_job_objects_and_persists_dicts_at_boundary(monkeypatch):
    class Browser:
        page = object()

        def start(self):
            pass

        def open(self, url):
            return self.page

        def close(self):
            pass

    class Extractor:
        def extract(self, page):
            return [{
                "title": "Data Analyst", "url": "https://example.test/data",
                "company": "Example", "location": "Remote",
            }]

    class Filter:
        def should_open(self, title):
            return {"open": True}

    class Parser:
        def parse(self, page):
            return {"skills": ["SQL"], "page_text": "Data Analyst uses SQL"}

    class Repository:
        def __init__(self):
            self.persisted = []

        def has_seen(self, url):
            return False

        def remember_job(self, job):
            self.persisted.append(job)

    repository = Repository()
    monkeypatch.setattr("modules.discovery.job_crawler.BrowserManager", Browser)
    monkeypatch.setattr("modules.discovery.job_crawler.JobLinkExtractor", Extractor)
    monkeypatch.setattr("modules.discovery.job_crawler.QuickFilter", Filter)
    monkeypatch.setattr("modules.discovery.job_crawler.ApplicationRepository", lambda: repository)

    crawler = JobCrawler(PROFILE)
    crawler.parser = Parser()
    jobs = crawler.crawl("https://boards.greenhouse.io/example")

    assert len(jobs) == 1
    assert isinstance(jobs[0], Job)
    assert jobs[0].description == "Data Analyst uses SQL"
    assert repository.persisted == [{
        "skills": ["SQL"], "page_text": "Data Analyst uses SQL",
        "title": "Data Analyst", "url": "https://example.test/data",
        "company": "Example", "location": "Remote",
    }]
