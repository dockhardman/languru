import copy
from pprint import pformat
from typing import List

import duckdb
import pytest

from languru.documents.document import Document
from languru.exceptions import NotFound

raw_docs = [
    {
        "name": "AMD's New AI Chips",
        "content": "AMD unveiled its latest AI chips, including the Instinct MI325X accelerator and 5th Gen EPYC processors, at its Advancing AI 2024 event, aiming to challenge Nvidia's dominance in the lucrative data center GPU market and compete with Intel in server CPUs. According to reports from Yahoo Finance and PYMNTS, while AMD's new offerings show improved performance, analysts suggest they still lag behind Nvidia's upcoming Blackwell chips by about a year.",  # noqa: E501
        "metadata": {"source": "Yahoo Finance"},
    },
    {
        "name": "Jupiter's 190 Year Old Storm",
        "content": "Jupiter's Great Red Spot, a colossal storm that has fascinated astronomers for centuries, is undergoing unexpected changes. Recent observations by the Hubble Space Telescope reveal that this 190-year-old vortex is oscillating in size and shape, behaving like a cosmic stress ball as it continues to shrink and evolve.",  # noqa: E501
    },
    {
        "name": "Tesla Unveiled Cybercab",
        "content": 'Tesla has unveiled its highly anticipated Cybercab robotaxi, showcasing a fleet of 20 sleek, autonomous vehicles at the "We, Robot" event held at Warner Bros. Discovery studio. As reported by TechCrunch, the Cybercab features a design reminiscent of a smaller Cybertruck, complete with suicide doors and no steering wheel or pedals, signaling Tesla\'s bold step towards a fully autonomous future.',  # noqa: E501
    },
]


def test_document_operations():
    conn: "duckdb.DuckDBPyConnection" = duckdb.connect(":memory:")

    # Touch table
    Document.objects.touch(conn=conn, debug=True)

    # Create documents
    docs: List["Document"] = []
    for _raw_doc in raw_docs:
        doc = Document.objects.create(
            Document.from_content(**_raw_doc), conn=conn, debug=True
        )
        docs.append(doc)

    # Get documents
    retrieved_docs = Document.objects.retrieve(
        docs[0].document_id, conn=conn, debug=True
    )
    assert retrieved_docs is not None
    assert retrieved_docs.document_id == docs[0].document_id
    after = None
    has_more = True
    docs_ids_set = set()
    while has_more:
        page_docs = Document.objects.list(after=after, conn=conn, debug=True, limit=1)
        after = page_docs.last_id
        has_more = len(page_docs.data) > 0
        docs_ids_set.update(doc.document_id for doc in page_docs.data)
    assert docs_ids_set == set(doc.document_id for doc in docs)

    # Update document
    new_doc_name = "[Updated] " + docs[0].name
    updated_doc = Document.objects.update(
        docs[0].document_id,
        name=new_doc_name,
        metadata={"written_by": "Languru"},
        conn=conn,
        debug=True,
    )
    new_meta = copy.deepcopy(docs[0].metadata)
    new_meta["written_by"] = "Languru"  # Merge strategy is update extra fields
    assert updated_doc.name == new_doc_name
    assert pformat(updated_doc.metadata) == pformat(new_meta)

    # Remove document
    Document.objects.remove(docs[0].document_id, conn=conn, debug=True)
    with pytest.raises(NotFound):
        Document.objects.retrieve(docs[0].document_id, conn=conn, debug=True)

    # Create document  again
    docs[0] = Document.objects.create(
        Document.from_content(**raw_docs[0]), conn=conn, debug=True
    )
