import json
import networkx as nx
from kiwipiepy import Kiwi
from krwordrank.word import KRWordRank
from collections import Counter
import os

# 이 파일은 텍스트에서 주요 키워드를 추출하는 기능을 담당합니다.
# Kiwi 형태소 분석기를 사용하여 명사를 추출하고, TextRank 알고리즘과 KR-WordRank를
# 사용하여 단어의 중요도를 평가합니다.
#
# 알고리즘 방법론:
# 1. 전처리 (Preprocessing): Kiwi 형태소 분석기를 사용하여 명사(NNG, NNP)를 추출하고, 지정된 불용어(stopwords)를 제거합니다.
# 2. TextRank: 단어 간의 동시 출현 관계를 그래프로 구성하고 PageRank 알고리즘을 적용하여 단어의 중요도를 계산합니다.
# 3. KR-WordRank: 비지도 학습 기반의 단어 추출 기법으로, 신조어나 복합 명사 등을 효과적으로 추출합니다.
# 4. 점수 결합 (Score Combination): TextRank와 KR-WordRank에서 산출된 점수를 각각 정규화(Normalize)한 후 합산합니다.
# 5. 제목 가중치 (Title Boost): 추출된 키워드가 기사의 제목에 포함되어 있을 경우, 해당 키워드의 중요도가 높다고 판단하여 점수에 1.5배의 가중치를 부여합니다.
#
# 최종적으로 계산된 통합 점수를 기준으로 상위 10개의 키워드를 선정하여 출력합니다.


class KeywordExtractor:
    def __init__(self):
        # 형태소 분석을 위해 Kiwi 초기화 (Pure Python/C++ 솔루션, JVM 불필요)
        self.kiwi = Kiwi()
        # 불용어 리스트: 키워드 추출에서 제외할 단어들
        self.stopwords = {"같은", "있다", "관련", "위한", "것으로", "반면", "이날", "상위"}

    def preprocess(self, text):
        """
        1단계: 조사 및 부사 필터링
        유지: NNG (일반 명사), NNP (고유 명사)
        제거: J (조사), MA (부사), E (어미)
        참고: Kiwi는 유사한 태그(NNG, NNP 등)를 사용합니다.
        불용어(stopwords)에 포함된 단어는 제외합니다.
        """
        if not text:
            return []

        try:
            # 토큰화
            tokens = self.kiwi.tokenize(text)

            # 태그 기반 필터링
            keywords = []
            for token in tokens:
                # 일반 명사(NNG)와 고유 명사(NNP)만 유지
                if token.tag in ["NNG", "NNP"]:
                    # 한 글자 단어 및 불용어 필터링
                    if len(token.form) > 1 and token.form not in self.stopwords:
                        keywords.append(token.form)

            return keywords
        except Exception as e:
            print(f"Error in preprocessing: {e}")
            return []

    def apply_textrank(self, tokens, window_size=3, top_k=5):
        """
        2단계: 반복 명사 가중치 부여 (TextRank)
        """
        if not tokens:
            return []

        # 고유 단어
        nodes = list(set(tokens))

        # 그래프 생성
        graph = nx.Graph()
        graph.add_nodes_from(nodes)

        # 동시 출현에 대한 간선 추가
        for i in range(len(tokens)):
            for j in range(i + 1, min(i + window_size, len(tokens))):
                w1 = tokens[i]
                w2 = tokens[j]
                if w1 != w2:
                    if graph.has_edge(w1, w2):
                        graph[w1][w2]["weight"] += 1
                    else:
                        graph.add_edge(w1, w2, weight=1)

        # PageRank 실행
        try:
            scores = nx.pagerank(graph)
            # 점수순 정렬
            ranked_keywords = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            return ranked_keywords[:top_k]
        except Exception as e:
            print(f"Error in TextRank: {e}")
            return []

    def extract_new_words(self, text, top_k=5):
        """
        3단계: KR-WordRank를 사용한 신조어 처리
        """
        if not text:
            return []

        # KRWordRank는 텍스트 리스트(문장들)를 필요로 함
        # 텍스트를 문장 단위로 분리 (줄바꿈 또는 문장부호로 간단 분리)
        sentences = text.replace(".", "\n").split("\n")
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return []

        try:
            min_count = 2  # 고려할 최소 빈도수
            max_length = 10
            verbose = False
            wordrank_extractor = KRWordRank(min_count=min_count, max_length=max_length, verbose=verbose)

            beta = 0.85  # PageRank 감쇠 계수
            max_iter = 10

            keywords, rank, graph = wordrank_extractor.extract(sentences, beta, max_iter)

            # 불용어 필터링
            filtered_keywords = {word: score for word, score in keywords.items() if word not in self.stopwords}

            # 순위/점수순 정렬
            sorted_keywords = sorted(filtered_keywords.items(), key=lambda x: x[1], reverse=True)
            return sorted_keywords[:top_k]
        except Exception as e:
            # 텍스트가 너무 짧거나 로직이 수렴하지 않으면 KRWordRank가 실패할 수 있음
            # print(f"정보: KRWordRank 건너뜀 또는 실패 (텍스트가 너무 짧을 수 있음): {e}")
            return []

    def extract_keywords(self, text, title=None, top_k=10):
        """
        단일 텍스트에서 키워드 추출 (TextRank + KR-WordRank + Title Boost)
        """
        if not text:
            return []

        # 1단계 및 2단계: TextRank 파이프라인 (상위 20개 후보 추출)
        tokens = self.preprocess(text)
        textrank_keywords = self.apply_textrank(tokens, top_k=20)

        # 3단계: 신조어 (KR-WordRank) (상위 20개 후보 추출)
        new_words = self.extract_new_words(text, top_k=20)

        # 결합 및 순위 지정
        combined_scores = {}

        # TextRank 점수 정규화 및 추가
        if textrank_keywords:
            max_tr = textrank_keywords[0][1]
            for word, score in textrank_keywords:
                norm_score = score / max_tr if max_tr > 0 else 0
                combined_scores[word] = combined_scores.get(word, 0) + norm_score

        # KR-WordRank 점수 정규화 및 추가
        if new_words:
            max_kr = new_words[0][1]
            for word, score in new_words:
                norm_score = score / max_kr if max_kr > 0 else 0
                combined_scores[word] = combined_scores.get(word, 0) + norm_score

        # 제목 가중치 적용: 키워드가 제목에 포함된 경우 점수 1.5배 증가
        if title:
            for word in combined_scores:
                if word in title:
                    combined_scores[word] *= 1.5

        # 결합된 점수순 정렬
        final_ranked = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)

        # 상위 top_k개 단어만 반환
        return [word for word, score in final_ranked[:top_k]]

    def process_file(self, file_path):
        print(f"Processing file: {file_path}")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                articles = json.load(f)

            results = []

            for article in articles:
                article_id = article.get("article_id", "N/A")
                title = article.get("title", "No Title")
                content = article.get("full_text", "") or article.get("short_text", "")  # 대체 텍스트

                # print(f"\n--- Article: {title} ---")
                if not content:
                    # print(f"(No content found in Article {article_id})")
                    continue

                # 1단계 및 2단계: TextRank 파이프라인 (상위 20개 후보 추출)
                tokens = self.preprocess(content)
                textrank_keywords = self.apply_textrank(tokens, top_k=20)

                # 3단계: 신조어 (KR-WordRank) (상위 20개 후보 추출)
                new_words = self.extract_new_words(content, top_k=20)

                # 결합 및 순위 지정
                combined_scores = {}

                # TextRank 점수 정규화 및 추가
                if textrank_keywords:
                    # 정렬되어 있으므로 첫 번째 항목이 최대 점수
                    max_tr = textrank_keywords[0][1]
                    for word, score in textrank_keywords:
                        norm_score = score / max_tr if max_tr > 0 else 0
                        combined_scores[word] = combined_scores.get(word, 0) + norm_score

                # KR-WordRank 점수 정규화 및 추가
                if new_words:
                    max_kr = new_words[0][1]
                    for word, score in new_words:
                        norm_score = score / max_kr if max_kr > 0 else 0
                        combined_scores[word] = combined_scores.get(word, 0) + norm_score

                # 제목 가중치 적용: 키워드가 제목에 포함된 경우 점수 1.5배 증가
                if title:
                    for word in combined_scores:
                        if word in title:
                            combined_scores[word] *= 1.5

                # 결합된 점수순 정렬
                final_ranked = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)

                # 출력 형식: 기사 [ID], 제목, 키워드1, 가중치, 키워드2, 가중치...
                # 상위 10개 키워드 출력
                top_final = final_ranked[:10]

                output_parts = [str(article_id), title]
                for word, weight in top_final:
                    output_parts.append(word)
                    output_parts.append(f"{weight:.4f}")

                output_string = ", ".join(output_parts)
                print(output_string)

                results.append(output_string)

            return results
        except Exception as e:
            print(f"Error processing file: {e}")
            return []


if __name__ == "__main__":
    extractor = KeywordExtractor()
    target_file = "sample_article_for_Keyword.json"

    # 현재 디렉토리에 파일이 있는지 확인, 없으면 backend/keyword_extractor에서의 상대 경로 시도
    if not os.path.exists(target_file):
        # 다른 곳에서 실행 중인 경우 알려진 구조를 기반으로 절대 경로 시도
        target_file = (
            r"c:\Users\201-05\Desktop\VaccineDailyReport-main\backend\keyword_extractor\sample_article_for_Keyword.json"
        )

    extractor.process_file(target_file)
