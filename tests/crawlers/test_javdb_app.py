import pytest

from mdcx.config.models import Website
from mdcx.crawlers.javdb_app import JavdbAPICrawler
from mdcx.models.types import CrawlerInput


def test_normalize_image_url_rewrites_legacy_host():
    crawler = JavdbAPICrawler(client=None)

    assert (
        crawler._normalize_image_url("https://tp.cmastd.com/rhe951l4q/covers/demo.jpg")
        == "https://c0.jdbstatic.com/covers/demo.jpg"
    )
    assert (
        crawler._normalize_image_url("https://tp.cmastd.com/rhe951l4q/small_covers/demo.jpg")
        == "https://c0.jdbstatic.com/thumbs/demo.jpg"
    )


@pytest.mark.asyncio
async def test_run_maps_cover_to_thumb_and_thumb_to_poster():
    class FakeClient:
        async def get_json(self, url: str, **kwargs):
            assert kwargs["headers"]["jdsignature"]
            if "/api/v2/search" in url:
                return (
                    {
                        "data": {
                            "movies": [
                                {
                                    "id": "movie-1",
                                    "number": "URE-018",
                                    "title": "Title",
                                }
                            ]
                        }
                    },
                    "",
                )

            if "/api/v4/movies/movie-1" in url:
                return (
                    {
                        "data": {
                            "movie": {
                                "id": "movie-1",
                                "number": "URE-018",
                                "title": "Title",
                                "origin_title": "Origin Title",
                                "summary": "Outline",
                                "cover_url": "https://tp.cmastd.com/rhe951l4q/covers/cover-wide.jpg",
                                "thumb_url": "https://tp.cmastd.com/rhe951l4q/small_covers/poster-tall.jpg",
                                "duration": 120,
                                "release_date": "2024-01-02",
                                "maker_name": "Maker",
                                "director_name": "Director",
                                "publisher_name": "Publisher",
                                "series_name": "Series",
                                "tags": [{"name": "Tag1"}],
                                "actors": [{"name": "Actor1"}],
                                "preview_images": [{"thumb_url": "https://tp.cmastd.com/rhe951l4q/samples/1.jpg"}],
                                "preview_video_url": "//video.example.com/trailer.mp4",
                            }
                        }
                    },
                    "",
                )

            raise AssertionError(f"unexpected url: {url}")

    crawler = JavdbAPICrawler(client=FakeClient())
    input_data = CrawlerInput.empty()
    input_data.number = "URE-018"

    response = await crawler.run(input_data)

    assert response.data is not None
    assert response.data.source == Website.JAVDB_APP.value
    assert response.data.number == "URE-018"
    assert response.data.title == "Title"
    assert response.data.originaltitle == "Origin Title"
    assert response.data.thumb == "https://c0.jdbstatic.com/covers/cover-wide.jpg"
    assert response.data.poster == "https://c0.jdbstatic.com/thumbs/poster-tall.jpg"
    assert response.data.extrafanart == ["https://c0.jdbstatic.com/samples/1.jpg"]
    assert response.data.trailer == "https://video.example.com/trailer.mp4"
    assert response.data.release == "2024-01-02"
    assert response.data.year == "2024"
