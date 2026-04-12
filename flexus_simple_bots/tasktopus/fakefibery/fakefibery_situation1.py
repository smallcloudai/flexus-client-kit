from flexus_simple_bots.tasktopus.fakefibery import fakefibery_fakemcp as ff


def build() -> ff.FakeFibery:
    return ff.FakeFibery(
        me_person_id="",
        people=[],
        boards=[],
        tasks=[],
        documents=[],
        activity=[],
    )
