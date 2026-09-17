from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from wagtail.models import Collection, GroupCollectionPermission, GroupPagePermission, Page

GROUPS = {
    "Administrateurs": Permission.objects.none,
    "Rédacteurs": Permission.objects.none,
    "Éditeurs": Permission.objects.none,
}


class Command(BaseCommand):
    help = "Crée les groupes éditoriaux et attribue des permissions CMS cohérentes."

    def handle(self, *args, **options):
        all_cms = Permission.objects.filter(
            content_type__app_label__in=[
                "content",
                "wagtailcore",
                "wagtailimages",
                "wagtaildocs",
                "wagtailadmin",
            ]
        )
        for name in GROUPS:
            group, _ = Group.objects.get_or_create(name=name)
            if name == "Administrateurs":
                permissions = all_cms
            elif name == "Éditeurs":
                permissions = all_cms.exclude(codename__startswith="delete_")
            else:
                permissions = all_cms.filter(codename__regex=r"^(add|change|view)_").exclude(
                    codename__in=["change_site", "change_redirect"]
                )
            group.permissions.set(permissions)

            page_codenames = ["add_page", "change_page"]
            if name in {"Administrateurs", "Éditeurs"}:
                page_codenames += ["publish_page", "lock_page", "unlock_page"]
            if name == "Administrateurs":
                page_codenames += ["delete_page", "bulk_delete_page"]
            GroupPagePermission.objects.filter(group=group).delete()
            root_page = Page.get_first_root_node()
            for permission in Permission.objects.filter(
                content_type__app_label="wagtailcore",
                content_type__model="page",
                codename__in=page_codenames,
            ):
                GroupPagePermission.objects.create(
                    group=group, page=root_page, permission=permission
                )

            library_actions = ["add", "change"]
            if name == "Administrateurs":
                library_actions.append("delete")
            library_permissions = Permission.objects.filter(
                content_type__app_label__in=["wagtailimages", "wagtaildocs"],
                codename__regex=rf"^({'|'.join(library_actions)})_",
            )
            GroupCollectionPermission.objects.filter(group=group).delete()
            root_collection = Collection.get_first_root_node()
            for permission in library_permissions:
                GroupCollectionPermission.objects.create(
                    group=group, collection=root_collection, permission=permission
                )
            self.stdout.write(self.style.SUCCESS(f"Groupe {name} configuré."))
