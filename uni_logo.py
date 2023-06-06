from pathlib import Path

import requests
from tqdm import tqdm


class UniRanking:
    def __init__(self):
        self.base_url = 'https://www.shanghairanking.com'
        self.api_url = f"{self.base_url}/api/pub/v1/arwu/rank?version=2022"
        self.rankings = None
        self.uni_rank = {}  # {uni_name: ranking}

    def get_uni_ranking(self) -> None:
        if not self.rankings:
            response = requests.get(self.api_url, timeout=5)
            data = response.json()
            self.rankings = data['data']['rankings']
        return self.rankings

    def download_uni_logo(self, num_uni=1000) -> None:
        if not self.rankings:
            self.get_uni_ranking()

        self._check_img_folder()

        for rank in tqdm(self.rankings[:num_uni]):
            uni_name, ranking_str, short_path = rank['univNameEn'], rank['ranking'], rank['univLogo']
            self.uni_rank[uni_name] = ranking_str

            rsp = requests.get(f"{self.base_url}/_uni/{short_path}", timeout=5)

            with open(Path.cwd() / "images" / f"{uni_name}{Path(short_path).suffix}", 'wb') as f:
                f.write(rsp.content)
        print("Done.")

    def _check_img_folder(self) -> None:
        folder_path = Path.cwd() / Path("images")
        if not folder_path.exists():
            folder_path.mkdir()
            print("Folder 'images' created.")
        else:
            print("Folder 'images' already exists.")


if __name__ == "__main__":
    uni_ranking = UniRanking()
    uni_ranking.download_uni_logo()
