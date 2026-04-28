import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from application.field_definitions.create_field_definition import create_field_definition
from application.field_definitions.schemas import CreateFieldDefinitionInput
from domain.field_definitions.entity import FieldDefinitionQueryParams, FieldType
from infrastructure.firebase import get_firestore_client
from infrastructure.persistence.firestore_common import get_timestamp
from infrastructure.persistence.firestore_field_definitions import (
    FirestoreFieldDefinitionRepository,
)


def _build_inputs() -> list[CreateFieldDefinitionInput]:
    return [
        CreateFieldDefinitionInput(
            key="text",
            label="Text",
            field_type=FieldType.TEXT,
            min_length=1,
            max_length=255,
        ),
        CreateFieldDefinitionInput(
            key="number",
            label="Number",
            field_type=FieldType.NUMBER,
        ),
        CreateFieldDefinitionInput(
            key="boolean",
            label="Boolean",
            field_type=FieldType.BOOLEAN,
        ),
        CreateFieldDefinitionInput(
            key="select",
            label="Select",
            field_type=FieldType.SELECT,
            options=["option_1", "option_2"],
        ),
        CreateFieldDefinitionInput(
            key="cpf",
            label="CPF",
            field_type=FieldType.TEXT,
            format="cpf",
        ),
        CreateFieldDefinitionInput(
            key="email",
            label="Email",
            field_type=FieldType.TEXT,
            format="email",
        ),
        CreateFieldDefinitionInput(
            key="phone",
            label="Phone",
            field_type=FieldType.TEXT,
            format="phone",
        ),
        CreateFieldDefinitionInput(
            key="url",
            label="URL",
            field_type=FieldType.TEXT,
            format="url",
        ),
        CreateFieldDefinitionInput(
            key="time_iso",
            label="Time ISO",
            field_type=FieldType.TEXT,
            format="time_iso",
        ),
        CreateFieldDefinitionInput(
            key="date_iso",
            label="Date ISO",
            field_type=FieldType.TEXT,
            format="date_iso",
        ),
        CreateFieldDefinitionInput(
            key="datetime_iso",
            label="Datetime ISO",
            field_type=FieldType.TEXT,
            format="datetime_iso",
        ),
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--created-by", default="seed-script")
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--no-skip-existing", dest="skip_existing", action="store_false")
    parser.set_defaults(skip_existing=True)
    args = parser.parse_args()

    db = get_firestore_client()
    repo = FirestoreFieldDefinitionRepository(db)
    existing = {
        row.key
        for row in repo.list(
            FieldDefinitionQueryParams(
                active=None,
                deleted=False,
                field_type=None,
                limit=None,
                offset=None,
            )
        )
    }
    created: list[str] = []
    skipped: list[str] = []
    now = get_timestamp()
    for item in _build_inputs():
        if args.skip_existing and item.key in existing:
            skipped.append(item.key)
            continue
        create_field_definition(repo, item, args.created_by, now)
        created.append(item.key)

    print(f"created={created}")
    print(f"skipped={skipped}")


if __name__ == "__main__":
    main()
