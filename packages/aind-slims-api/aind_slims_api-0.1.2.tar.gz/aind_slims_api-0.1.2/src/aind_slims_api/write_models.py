"""Model writing utilities adding records to the SLIMS database.

Notes
-----
- Here due to restructuring of models, will likely be deprecated in the future.
"""

import logging

from aind_slims_api.core import SlimsClient
from aind_slims_api.models import (
    SlimsBehaviorSession,
    SlimsInstrument,
    SlimsMouseContent,
    SlimsUser,
)

logger = logging.getLogger()


def write_behavior_session_content_events(
    client: SlimsClient,
    mouse: SlimsMouseContent,
    instrument: SlimsInstrument,
    trainers: list[SlimsUser],
    *behavior_sessions: SlimsBehaviorSession,
) -> list[SlimsBehaviorSession]:
    """Writes behavior sessions to the SLIMS database.

    Notes
    -----
    - Here due to restructuring of models, will likely be deprecated in the
     future.
    """
    trainer_pks = [trainer.pk for trainer in trainers]
    logger.debug(f"Trainer pks: {trainer_pks}")
    added = []
    for behavior_session in behavior_sessions:
        updated = behavior_session.model_copy(
            update={
                "mouse_pk": mouse.pk,
                "instrument": instrument.pk,
                "trainers": trainer_pks,
            },
        )
        logger.debug(f"Resolved behavior session: {updated}")
        added.append(client.add_model(updated))

    return added
