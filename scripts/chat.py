from scripts.game_rules import TEXT_TO_EMOTE


class Chat:
    @staticmethod
    def process(message: str):

        for keyword in TEXT_TO_EMOTE:
            message = message.replace(keyword, f'([{{{ keyword }}}])')
        for keyword in TEXT_TO_EMOTE:
            html = f'<img class="emo-ticon" src="{TEXT_TO_EMOTE[keyword]}" title="{keyword}">'
            message = message.replace(f'([{{{keyword}}}])', html)

        return message
