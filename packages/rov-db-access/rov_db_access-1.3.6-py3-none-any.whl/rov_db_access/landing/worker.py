from datetime import datetime
from typing import TypedDict
from sqlalchemy.orm import Session
from sqlalchemy import select
from rov_db_access.config.db_utils import init_db_engine
from rov_db_access.config.settings import Settings
from rov_db_access.utils.utils import wkbelement_to_wkt

from rov_db_access.landing.models import Articles, Members, Newsletter, Subscribers

settings = Settings()

SaveNewsletterDict = TypedDict("SaveNewsletterDict", {
    "title": str,
    "content": str,
    "date": str,
    "author": str,
    "is_published": bool
})


class LandingWorker:

    def __init__(self) -> None:
        self.engine = init_db_engine(
            settings.db_rov_proxy_user,
            settings.db_rov_proxy_password,
            settings.db_rov_proxy_host,
            settings.db_rov_proxy_port,
            settings.db_rov_landing_database
        )

    def load_articles(self):
        with Session(self.engine) as session:
            articles_query = (
                select(Articles)
                .order_by(Articles.date.desc())
                .limit(3)
            )
            articles = session.execute(articles_query).all()
            result = []
            for article in articles:
                article = article[0]
                wkt = None
                if article.location is not None:
                    wkt = wkbelement_to_wkt(article.location)
                result.append({
                    "id": article.id,
                    "title": article.title,
                    "content": article.content,
                    "location": wkt,
                    "zoom": article.zoom,
                    "date": article.date
                })
            return result

    def load_members(self):
        with Session(self.engine) as session:
            members_query = (
                select(Members)
                .order_by(Members.order)
            )
            members = session.execute(members_query).all()
            result = []
            for member in members:
                member = member[0]
                result.append({
                    "id": member.id,
                    "name": member.name,
                    "profession": member.profession,
                    "description": member.description,
                    "photo_url": member.photo_url,
                    "linkedin": member.linkedin,
                    "github": member.github,
                    "order": member.order,
                    "job": member.job,
                })
            return result

    def load_newsletter(self):
        with Session(self.engine) as session:
            newsletter_query = (
                select(Newsletter)
                .order_by(Newsletter.date.desc())
            )
            newsletter = session.execute(newsletter_query).all()
            result = []
            for new in newsletter:
                new = new[0]
                result.append({
                    "id": new.id,
                    "title": new.title,
                    "content": new.content,
                    "author": new.author,
                    "is_published": new.is_published,
                    "date": new.date
                })
            return result

    def get_article(self, id: int):
        with Session(self.engine) as session:
            news_query= (
                select(Newsletter)
                .where(Newsletter.id == id)
                .limit(1)
            )
            article = session.scalar(news_query)
            if article is None:
                return {}
            print(f'found article with id: {id}')
            return {
                "id": article.id,
                "title": article.title,
                "content": article.content,
                "author": article.author,
                "is_published": article.is_published,
                "date": article.date
            }

    def update_article(self, id: int, data: SaveNewsletterDict):
        with Session(self.engine) as session:
            news_query = (
                select(Newsletter)
                .where(Newsletter.id == id)
                .limit(1)
            )
            article = session.scalar(news_query)
            if article is None:
                return {}
            datetime_object = datetime.strptime(data["date"], '%d/%m/%Y')
            article.title = data["title"]
            article.content = data["content"]
            article.date = datetime_object
            article.author = data["author"]
            article.is_published = data["is_published"]
            session.commit()
            return article

    def add_subscriber(self, name: str, email: str):
        with Session(self.engine) as session:
            new_subscriber = Subscribers(name=name, email=email)
            session.add(new_subscriber)
            session.commit()
            return new_subscriber

    def save_newsletter(self, data: SaveNewsletterDict):
        with Session(self.engine) as session:
            datetime_object = datetime.strptime(data["date"], '%d/%m/%Y')
            new_newsletter = Newsletter(
                title=data["title"],
                content=data["content"],
                date=datetime_object,
                author=data["author"],
                is_published=data["is_published"]
            )
            session.add(new_newsletter)
            session.commit()
            return new_newsletter

    def delete_article(self, id: int):
        with Session(self.engine) as session:
            news_query = (
                select(Newsletter)
                .where(Newsletter.id == id)
                .limit(1)
            )
            article = session.scalar(news_query)
            if article is None:
                return {}
            session.delete(article)
            session.commit()
            return article
