from django.contrib.auth.models import User
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import InlinePanel, FieldPanel, PageChooserPanel
from wagtail.core.fields import RichTextField

from wagtail.core.models import Page, Orderable
from wagtail.images.edit_handlers import ImageChooserPanel


class CarouselItem(Orderable):
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    caption = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=255, blank=True)
    page = ParentalKey('HomePage', related_name='carousel_items')
    link = models.ForeignKey('wagtailcore.Page', on_delete=models.SET_NULL, null=True, blank=True)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
        FieldPanel('title'),
        PageChooserPanel('link'),
    ]


class HomePage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        InlinePanel('carousel_items', label="Carousel Items"),
        FieldPanel('intro', classname="full"),
    ]

    class Meta:
        verbose_name = "Homepage"


class ProductDetail(Orderable):
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    caption = models.CharField(max_length=255, blank=True)
    info = RichTextField(blank=True)
    page = ParentalKey('ProductPage', related_name='product_details')

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
        FieldPanel('info'),
    ]


class ProductPage(Page):
    caption = models.CharField(max_length=255, blank=True)
    general_info = RichTextField(blank=True)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    content_panels = Page.content_panels + [
        ImageChooserPanel('image'),
        InlinePanel('product_details', label="Product Details"),
        FieldPanel('caption'),
        FieldPanel('general_info'),
    ]

    class Meta:
        verbose_name = "Productpage"
