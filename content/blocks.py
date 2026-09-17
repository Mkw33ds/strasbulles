from wagtail import blocks
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock


class LinkBlock(blocks.StructBlock):
    label = blocks.CharBlock(label="Libellé")
    page = blocks.PageChooserBlock(required=False, label="Page interne")
    url = blocks.URLBlock(required=False, label="Lien externe")

    class Meta:
        icon = "link"
        label = "Bouton ou lien"


class GalleryImageBlock(blocks.StructBlock):
    image = ImageChooserBlock(label="Image")
    alternative_text = blocks.CharBlock(
        label="Texte alternatif",
        help_text="Décrivez l’information portée par l’image. Laissez vide si elle est décorative.",
        required=False,
    )
    caption = blocks.CharBlock(label="Légende", required=False)


class BaseStreamBlock(blocks.StreamBlock):
    heading = blocks.CharBlock(label="Titre", icon="title")
    rich_text = blocks.RichTextBlock(
        label="Texte enrichi",
        features=["h2", "h3", "bold", "italic", "ol", "ul", "link", "document-link"],
    )
    image = GalleryImageBlock(label="Image", icon="image")
    gallery = blocks.ListBlock(GalleryImageBlock(), label="Galerie", icon="image")
    quote = blocks.StructBlock(
        [
            ("text", blocks.TextBlock(label="Citation")),
            ("author", blocks.CharBlock(label="Auteur ou source", required=False)),
        ],
        label="Citation",
        icon="openquote",
    )
    call_to_action = blocks.StructBlock(
        [
            ("title", blocks.CharBlock(label="Titre")),
            ("text", blocks.TextBlock(label="Texte", required=False)),
            ("link", LinkBlock()),
        ],
        label="Appel à l’action",
        icon="pick",
    )
    document = blocks.StructBlock(
        [
            ("document", DocumentChooserBlock(label="Document")),
            ("label", blocks.CharBlock(label="Libellé")),
        ],
        label="Document à télécharger",
        icon="doc-full",
    )
    columns = blocks.StructBlock(
        [
            ("left", blocks.RichTextBlock(label="Colonne gauche")),
            ("right", blocks.RichTextBlock(label="Colonne droite")),
        ],
        label="Deux colonnes",
        icon="grip",
    )


class ProgrammeBlock(blocks.StructBlock):
    time = blocks.CharBlock(label="Horaire", required=False)
    title = blocks.CharBlock(label="Titre")
    text = blocks.TextBlock(label="Détails", required=False)

    class Meta:
        label = "Élément de programme"
        icon = "date"
