import factory
import faker
from factory.fuzzy import BaseFuzzyAttribute
from wagtail.documents import get_document_model
from wagtail.images import get_image_model
from wagtail.models import Page

from coop.utils.testdata import rbool

fake = faker.Faker("en_AU")
Image = get_image_model()
Document = get_document_model()


class FuzzyImage(BaseFuzzyAttribute):
    def fuzz(self) -> Image | None:
        return Image.objects.order_by("?").first()


class FuzzyPage(BaseFuzzyAttribute):
    def fuzz(self) -> Page | None:
        return Page.objects.order_by("?").first()


class FuzzyDocument(BaseFuzzyAttribute):
    def fuzz(self) -> Document:
        return Document.objects.order_by("?").first()


class FuzzyParagraphs(factory.Faker):
    def __init__(self, num=1, **kwargs):
        super().__init__("paragraphs", nb=num, **kwargs)

    def evaluate(self, instance, step, extra) -> str:
        value = super().evaluate(instance, step, extra)
        return "".join(f"<p>{p}</p>" for p in value)


class FuzzyWords(factory.Faker):
    def __init__(self, nb_words: int = 1, maybe: bool = False, variable_length: bool = True):
        self.maybe = maybe
        super().__init__("sentence", nb_words=nb_words, variable_nb_words=variable_length)

    def evaluate(self, instance, step, extra) -> str:
        if self.maybe and not rbool():
            return ""
        # create a variable sentence, remove full stop
        value = super().evaluate(instance, step, extra)
        return value[:-1]
