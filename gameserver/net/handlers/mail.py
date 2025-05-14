from proto import *
from gameserver.util import cur_timestamp_secs


async def on_get_mail_cs_req(
    _session: "PlayerSession", _req: GetMailCsReq, res: GetMailScRsp
) -> None:
    cur_time = cur_timestamp_secs()

    res.is_end = True
    res.mail_list = [
        ClientMail(
            title="Welcome!",
            sender="Server",
            content="Welcome!",
            id=1,
            is_read=False,
            time=cur_time - 31536000,
            expire_time=cur_time + 31536000,
            mail_type=MailType.MAIL_TYPE_NORMAL,
            attachment=ItemList(
                item_list_=[
                    Item(
                        item_id=1310,
                        level=80,
                        num=1,
                    )
                ]
            ),
        )
    ]
