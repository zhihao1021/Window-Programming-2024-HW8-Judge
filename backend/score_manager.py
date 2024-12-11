from csv import reader, writer


class ScoreManager():
    data: dict[str, list[int, int, int, int]]

    def __init__(self):
        with open("score.csv", newline="", encoding="utf-8") as score_file:
            self.data = {
                sid: list(map(int, score))
                for sid, *score in reader(score_file.readlines())
            }

    def get_scores(self, sid: str) -> tuple[int, int, int, int]:
        sid = sid.upper()
        return tuple(self.data.get(sid, (0, 0, 0, 0)))

    def update(
        self,
        sid: str,
        index: int,
        value: int
    ):
        sid = sid.upper()
        if self.data.get(sid) is None or index not in range(4):
            return

        if value < self.data[sid][index]:
            return

        self.data[sid][index] = value
        with open("score.csv", "w", newline="", encoding="utf-8") as score_file:
            csv_writer = writer(score_file)
            csv_writer.writerows([
                [key, *value]
                for key, value in self.data.items()
            ])


SCORE_MANAGER = ScoreManager()
