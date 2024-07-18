from transformers import AutoTokenizer, AutoModel, AutoModelForCausalLM, TextIteratorStreamer
from IPython.core.magic import register_line_magic, register_cell_magic, register_line_cell_magic
from IPython.display import display, Markdown, clear_output, HTML, update_display
from IPython import get_ipython
import torch
import pandas as pd
import ast
import numpy as np
from threading import Thread
import time
from rank_bm25 import BM25Okapi
import nltk
from nltk.tokenize import word_tokenize
from huggingface_hub import login
import random
import ipywidgets as widgets
import json

from langchain_openai import OpenAI, ChatOpenAI

# Necessary so that query embedding match (initialization) the pre-computed corpus embeddings
torch.manual_seed(0)
np.random.seed(0)

#########################################################################################################################################

class UPSayAI:
    def __init__(self, model_name="aristote/llama", model_access_token=None, model_temperature=0.8, model_max_tokens=2048, rag_model="dpr", rag_min_relevance=0.5, rag_max_results=5, recommendation_min_relevance=0.7, quiz_difficulty="moyen", quiz_min_relevance=0.2, quiz_max_results=100, num_questions_quiz=5, course_corpus_file="corpus_ISD.csv"):
        self.model_name = model_name
        self.model_access_token = model_access_token
        self.model_temperature = model_temperature
        self.model_max_tokens = int(model_max_tokens)
        self.rag_model = rag_model
        self.rag_min_relevance = rag_min_relevance
        self.rag_max_results = int(rag_max_results)
        self.recommendation_min_relevance = recommendation_min_relevance
        self.quiz_difficulty = quiz_difficulty
        self.quiz_min_relevance = quiz_min_relevance
        self.quiz_max_results = int(quiz_max_results)
        self.num_questions_quiz = int(num_questions_quiz)
        self.course_corpus_file = course_corpus_file


        self.check_values()
        
        self.config_rag()
        self.config_llm()

        self.setup_magics()

    # Check if the values are in the expected range of possible values
    def check_values(self):
        assert self.model_name in ["aristote/llama", "aristote/mixtral", "huggingface/llama"], "Invalid model_name. Current supported values are 'aristote/llama', 'aristote/mixtral', or 'huggingface/llama'"
        assert 0 <= self.model_temperature <= 1, "Invalid model_temperature. The temperature value has to be a float between 0 and 1"
        assert 512 <= self.model_max_tokens <= 4096, "Invalid model_max_tokens. The model_max_tokens value has to be an int between 512 and 4096"
        assert self.rag_model in ["dpr", "bm25"], "Invalid rag_model. Current supported values are 'dpr' or 'bm25'"
        assert 0 <= self.rag_min_relevance <= 1, "Invalid rag_min_relevance. The rag_min_relevance value has to be a float between 0 and 1"
        assert 1 <= self.rag_max_results <= 100, "Invalid rag_max_results. The rag_max_results value has to be an int between 1 and 100"
        assert 0 <= self.recommendation_min_relevance <= 1, "Invalid recommendation_min_relevance. The recommendation_min_relevance value has to be a float between 0 and 1"
        assert self.quiz_difficulty in ["facile", "moyen", "difficile"], "Invalid quiz_difficulte. Current supported values are 'facile', 'moyen', or 'difficile'"
        assert 0 <= self.quiz_min_relevance <= 1, "Invalid quiz_min_relevance. The quiz_min_relevance value has to be a float between 0 and 1"
        assert 10 <= self.quiz_max_results <= 1000, "Invalid quiz_max_results. The quiz_max_results value has to be an int between 10 and 1000"
        assert 3 <= self.num_questions_quiz <= 10, "Invalid num_questions_quiz. The num_questions_quiz value has to be an int between 3 and 10"


    # Config the RAG models and load 
    def config_rag(self):
        if self.rag_model == "dpr":
            self.load_corpus_embeddings()
            self.config_query_embedding()
        elif self.rag_model == "bm25":
            self.config_bm25()

    # Config the LLMs (using the config_llm_aristote or config_llm_huggingface functions) and define the persona prompts (role system)
    def config_llm(self):
        if self.model_name == "aristote/llama" or self.model_name == "aristote/mixtral":
            self.config_llm_aristote()
        elif self.model_name == "huggingface/llama":
            self.config_llm_huggingface()
            
        # Configure prompts for the LLMs
        
        # QR (for %ai_question)
        self.persona_prompt_qa = "Vous êtes un assistant virtuel qui aide les étudiants de l'Université Paris-Saclay avec des questions dans le domaine de la programmation et de la science des données, en répondant toujours de manière pédagogique et polie. Lorsque c'est possible, essayez d'utiliser des informations et des exemples tirés du matériel de cours pour aider l'étudiant à comprendre, en soulignant dans votre explication où l'étudiant a vu ce contenu être employé pendant le cours et en mettant toujours en contexte pour une réponse bien structurée. N'incluez pas d'images ou de médias dans votre réponse, uniquement du texte en format markdown."
        self.messages_history = []
        
        # Code generation (for %ai_code)
        self.persona_prompt_code = "Vous êtes un assistant virtuel qui écrit des codes python selon les instructions d'un étudiant de l'Université Paris-Saclay. Utilisez toujours des commentaires et documentez bien vos codes pour les rendre faciles à comprendre pour l'étudiant. Mettez toujours tout le code, y compris les éventuels exemples pratiques d'utilisation, dans un seul bloc délimité par '```python' au début et '```' à la fin. Ne générez pas plus d'un bloc de code, générez toujours un seul bloc avec tout le code et les exemples d'utilisation à l'intérieur afin que l'étudiant puisse tout exécuter dans une seule cellule jupyter. Utilisez des bibliothèques et des fonctions avec lesquelles l'étudiant est plus susceptible d'être familier, donnez la préférence à des solutions plus simples tant qu'elles sont correctes et entièrement fonctionnelles. Assurez-vous que votre code est correct, fonctionnel et que les éventuels exemples d'utilisation fonctionneront parfaitement et donneront des résultats corrects lorsqu'ils seront exécutés par l'étudiant. Terminez toujours par un court paragraphe après le bloc de code python (délimité par '```python' au début et '```') avec une description textuelle et des explications pour l'étudiant afin d'améliorer sa compréhension du sujet et du code généré."

        # Quiz (for %ai_quiz)
        # If student chooses a specific subject for the quiz (will be used in the instructions_prompt inside the ai_quiz function)
        self.quiz_subject = ""
        # The relevant cours content (cells from the notebooks) (is updated by the get_quiz_context function at every query)
        self.cours_content = ""
        # For prompt engineering, to help the LLM to understand the expected difficulty level
        if(self.quiz_difficulty == "facile"):
            self.quiz_level = "licence L1"
        elif(self.quiz_difficulty == "moyen"):
            self.quiz_level = "licence L3"
        elif(self.quiz_difficulty == "difficile"):
            self.quiz_level = "master M1"
        
        self.persona_prompt_quiz = f"Vous êtes un générateur de quiz style QCM de niveau de difficulté {self.quiz_difficulty} pour des étudiants de {self.quiz_level} qui souhaitent tester leurs connaissances dans le cadre de leurs études et de leur préparation aux examens. Le quiz a {self.num_questions_quiz} questions en français, où chaque question n'a qu'une seule réponse correcte et trois réponses incorrectes. Essayez de rédiger les quatre choix de réponses de longueur similaire pour éviter que la bonne réponse soit toujours la plus longue." + """ Organisez les questions générées dans une liste de dictionnaires python, où chaque dictionnaire représente une question formatée comme suit : [{"énoncé": "Question à l'élève (1) ?", "bonne_réponse": "Ceci est la réponse correcte à la question 1.", "mauvaises_réponses":["Ceci est la première réponse incorrecte à la question 1.", "Ceci est la deuxième réponse incorrecte à la question 1.", "Ceci est la troisième réponse incorrecte à la question 1."]}, {"énoncé": "Question à l'élève (2) ?", "bonne_réponse": "Ceci est la réponse correcte à la question 2.", "mauvaises_réponses":["Ceci est la première réponse incorrecte à la question 2.", "Ceci est la deuxième réponse incorrecte à la question 2.", "Ceci est la troisième réponse incorrecte à la question 2."]}, ...].""" + f" Cours à utiliser pour générer le quiz : {self.cours_content}"

        
        # Code explanation (for %ai_explain)
        self.persona_prompt_explain = "Vous êtes un assistant virtuel qui explique des codes python à un étudiant de l'Université Paris-Saclay d'une manière claire et informative. Fournissez une analyse textuelle complète en français du code que vous sera donné, en expliquant son objectif global, la logique utilisée, les principales variables, les bibliothèques et les fonctions utilisées par le programmeur, et les éventuels outputs attendus s'il y en a. Vous pouvez utiliser des extraits du code dans votre explication, délimité par '```python' au début et '```' à la fin, si vous pensez que cela aidera la compréhension de l'étudiant, et inclure des exemples possibles de quand et comment le code pourrait être utilisé par l'étudiant. Préférez expliquer l'objectif global et la logique dans un flux continu à travers un paragraphe plutôt que d'utiliser des sous-titres, mais énumérez les principales variables sous forme de puces. L'étudiant doit être en mesure de comprendre pleinement le code après avoir lu votre explication. Terminez toujours par une conclusion résumant l'explication. Rédigez toute votre explication en français."


        # Code debugging (for %ai_debug)
        self.persona_prompt_debug = "Vous êtes un assistant virtuel qui aide les étudiants de l'Université Paris-Saclay à déboguer des codes Python qui ne s'exécutent pas. Analysez le code et le message d'erreur que vous seront donnés, en générant un rapport de débogage avec une analyse textuelle expliquant les raisons qui causent les erreurs d'exécution indiquées par le message d'erreur. Enfin, proposez des solutions, délimitées par '```python' au début et '```' à la fin, que l'étudiant peut implémenter dans le code pour le corriger afin qu'il s'exécute correctement sans erreurs."
        

    # Load corpus contents and embeddings from CSV file
    def load_corpus_embeddings(self):
        try:
            self.df = pd.read_csv(self.course_corpus_file)
        except:
            raise ValueError("Course corpus CSV file not found.")
        try:
            self.df['embeddings'] = self.df['embeddings'].apply(ast.literal_eval)
            self.df['embeddings'] = self.df['embeddings'].apply(lambda x: torch.from_numpy(np.array(x)))
            self.df = self.df[self.df["content"].apply(lambda x: isinstance(x, str))].reset_index(drop=True)
            self.corpus_embeddings = self.df["embeddings"].tolist()
            self.corpus_embeddings = torch.stack([doc for doc in self.corpus_embeddings])
            self.corpus_embeddings = self.corpus_embeddings.float()
        except:
            raise ValueError("Course corpus file does not contain expected columns")

    # Query embedding tokenizer and model from HuggingFace. Only called if rag_model="dpr". 
    def config_query_embedding(self):
        self.tokenizer_dpr = AutoTokenizer.from_pretrained("etalab-ia/dpr-question_encoder-fr_qa-camembert",  do_lower_case=True, resume_download=None)
        self.model_dpr = AutoModel.from_pretrained("etalab-ia/dpr-question_encoder-fr_qa-camembert", return_dict=True, resume_download=None)

    # Confif BM25 retrieval
    def config_bm25(self):
        try:
            self.df = pd.read_csv(self.course_corpus_file)
            self.df = self.df[self.df["content"].apply(lambda x: isinstance(x, str))].reset_index(drop=True)
        except:
            raise ValueError("Course corpus file file not found.")
        try:
            self.bm25_index = BM25Okapi(self.df.tokenized_content.tolist())
        except:
            raise ValueError("Course corpus file does not contain expected columns")
    
    # Config LLM for aristote models
    def config_llm_aristote(self):
        if self.model_name == "aristote/llama":
            self.model = ChatOpenAI(openai_api_base = "https://dispatcher.aristote.centralesupelec.fr/v1", openai_api_key = self.model_access_token, model = "casperhansen/llama-3-70b-instruct-awq", temperature=self.model_temperature, max_tokens=self.model_max_tokens)
        elif self.model_name == "aristote/mixtral":
            self.model = ChatOpenAI(openai_api_base = "https://dispatcher.aristote.centralesupelec.fr/v1", openai_api_key = self.model_access_token, model = "casperhansen/mixtral-instruct-awq", temperature=self.model_temperature, max_tokens=self.model_max_tokens)

    # Config LLM for huggingface models (currently only Meta-Llama-3-8B-Instruct)
    def config_llm_huggingface(self):
        login(token=self.model_access_token)
        model_id = "meta-llama/Meta-Llama-3-8B-Instruct"
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
                    model_id,
                    torch_dtype=torch.bfloat16
                )
        
        self.model.to(self.device)
        
        self.terminators = [
                        self.tokenizer.eos_token_id,
                        self.tokenizer.convert_tokens_to_ids("<|eot_id|>")
                    ]
        
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        # Configure streamer for token-by-token display
        self.streamer = TextIteratorStreamer(self.tokenizer, skip_prompt = True)

    
        
    # Function to compute query embedding from the raw text (string)
    def get_query_embedding(self, text):
        input_ids = self.tokenizer_dpr(
            text, 
            return_tensors='pt',
            max_length = 512,
            truncation=True  # Truncate sequences longer than the maximum length
        )["input_ids"]
        embeddings = self.model_dpr.forward(input_ids).pooler_output
        return embeddings

    # Function to calculate cosine similarity between query embedding and every corpus cell embedding
    def cos_sim(self, a, b):
        a_norm = torch.nn.functional.normalize(a, p=2, dim=1)
        b_norm = torch.nn.functional.normalize(b, p=2, dim=1)
        return torch.mm(a_norm, b_norm.transpose(0, 1))

    # Function that generates the context to be passed as RAG to the LLM (context = concatenation of relevant cell contents)
    def get_context(self, query):
        if self.rag_model == "dpr":
            index_high_score = self.dpr_search(query, self.rag_min_relevance, self.rag_max_results)
        elif self.rag_model == "bm25":
            index_high_score = self.bm25_search(query)
        if(len(index_high_score) > 0):
            rag_content = "\n".join(self.df["content"].iloc[index_high_score])
            return rag_content
        return "Aucun extrait du support de cours n'a été trouvé contenant des informations pertinentes sur la question posée par l'étudiant. Si vous ne connaissez pas non plus la réponse, informez l'étudiant que vous n'avez trouvé aucune information sur ce qui lui est demandé et recommandez-lui de contacter les professeurs responsables du cours."

    # Function that generates the reading recommendations (notebooks from the course Gitlab that are relevant and the student should review) as hyperlinks
    def get_recommendation(self, query_answer):
        if self.rag_model == "dpr":
            index_high_score = self.dpr_search(query_answer, self.recommendation_min_relevance, self.rag_max_results)
        elif self.rag_model == "bm25":
            index_high_score = self.bm25_search(query_answer)
        if(len(index_high_score) > 0):
            rag_courses =  self.df["file"].iloc[index_high_score].unique().tolist()
            rag_weeks =  self.df["folder"].iloc[index_high_score].unique().tolist()
            rag_recommendation = ", ".join([f"[`{rag_courses[i][:-3]}`](https://gitlab.dsi.universite-paris-saclay.fr/L1InfoInitiationScienceDonnees/Instructors/-/blob/main/{rag_weeks[i]}/{rag_courses[i]})" for i in range(len(rag_courses))])
            return rag_recommendation
        return None

    # Function that generates the context to be passed as RAG to the LLM (context = concatenation of relevant cell contents)
    def get_quiz_context(self, query):
        if(query == ""):
            file_list = self.df.file.unique().tolist()
            file_list_filtered = [file for file in file_list if file != "CM1_1_presentation_UE.md"]
            notebook = random.choice(file_list_filtered)
            self.quiz_subject = ""
            return "\n".join(self.df[self.df["file"] == notebook]["content"].dropna())
        elif(query in self.df.file.unique().tolist()):
            self.quiz_subject = ""
            return "\n".join(self.df[self.df["file"] == query]["content"].dropna())
        elif(query in [x.replace(".md", "") for x in self.df.file.unique().tolist()]):
            self.quiz_subject = ""
            return "\n".join(self.df[self.df["file"] == query+".md"]["content"].dropna())
        else:
            if self.rag_model != "dpr":
                return "error_rag"
            else:
                # For now, check if there are at least 3 cells with similarity above 0.35 to see if subject is related to the class
                check_subject_relevance = self.dpr_search(query, 0.35, 5)
                if(len(check_subject_relevance) > 3):
                    index_high_score = self.dpr_search(query, self.quiz_min_relevance, self.quiz_max_results)
                    self.quiz_subject = query
                    return "\n".join(self.df["content"].iloc[index_high_score])
                return None

    # IR function based on DPR to find relevant extracts
    def dpr_search(self, search_string, threshold, max_results):
        query_embedding = self.get_query_embedding(search_string)
        cos_scores = self.cos_sim(query_embedding, self.corpus_embeddings)[0]
        cos_scores_np = (-1) * np.sort(-cos_scores.detach().numpy())
        cos_idx_np = np.argsort(-cos_scores.detach().numpy())
        mask = cos_scores_np > threshold
        index_high_score = cos_idx_np[mask][:max_results]
        return index_high_score

    # IR function based on BM25 to find relevant extracts
    def bm25_search(self, search_string):
        search_tokens = word_tokenize(search_string)
        scores = self.bm25_index.get_scores(search_tokens)
        top_indexes = np.argsort(scores)[::-1][:self.rag_max_results]
        return top_indexes

    # LLM Generation function for aristote models
    def aristote_generate(self, messages, initial_response):
        generated_text = initial_response
        for chunk in self.model.stream(messages):
            generated_text += chunk.content
            #display(Markdown(generated_text), clear=True)
            update_display(Markdown(generated_text), display_id=self.display_output.display_id)
        return generated_text

    # LLM Generation function for huggingface models
    def huggingface_generate(self, messages, initial_response):
        # Preprocess the question
        input_ids = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(self.device)
        
        generation_kwargs = {
            "input_ids": input_ids,
            "max_new_tokens": self.model_max_tokens,
            "eos_token_id": self.terminators,
            "pad_token_id": self.tokenizer.pad_token_id,
            "do_sample": True,
            "temperature": self.model_temperature,
            "top_p": 0.9,
            "streamer": self.streamer
        }
        # Generate answer and display it word by word as it is written (similar to ChatGPT user experience)
        thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
        thread.start()
        generated_text = initial_response
        for new_text in self.streamer:
            generated_text += new_text.replace("<|eot_id|>", "")
            #display(Markdown(generated_text), clear = True)
            update_display(Markdown(generated_text), display_id=self.display_output.display_id)
        return generated_text

    # LLM Quiz Generation function for aristote models
    def generate_quiz_questions_aristote(self):
        chunks = ""
        for chunk in self.model.stream(self.quiz_messages):
            chunks += chunk.content
            if "{" in chunks and "}" in chunks:
                init = chunks.find("{")
                end = chunks.find("}") + 1
                dict_string = chunks[init:end]
                try:
                    true_dict = json.loads(dict_string)
                    answers = [true_dict["bonne_réponse"]] + true_dict["mauvaises_réponses"]
                    random.shuffle(answers)
                    true_dict["toutes_réponses"] = answers
                    self.questions_llm.append(true_dict)
                except:
                    self.num_questions -= 1
                chunks = ""

    # LLM Quiz Generation function for huggingface models
    def generate_quiz_questions_huggingface(self):

        # Preprocess the question
        input_ids = self.tokenizer.apply_chat_template(
            self.quiz_messages,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(self.device)
        
        generation_kwargs = {
            "input_ids": input_ids,
            "max_new_tokens": 2048,
            "eos_token_id": self.terminators,
            "pad_token_id": self.tokenizer.pad_token_id,
            "do_sample": True,
            "temperature": self.model_temperature,
            "top_p": 0.9,
            "streamer": self.streamer
        }
        # Generate answer and display it word by word as it is written (similar to ChatGPT user experience)
        thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
        thread.start()

        generated_text = ""
        for new_text in self.streamer:
            generated_text += new_text.replace("<|eot_id|>", "")
            if "{" in generated_text and "}" in generated_text:
                init = generated_text.find("{")
                end = generated_text.find("}") + 1
                dict_string = generated_text[init:end]
                try:
                    true_dict = json.loads(dict_string)
                    answers = [true_dict["bonne_réponse"]] + true_dict["mauvaises_réponses"]
                    random.shuffle(answers)
                    true_dict["toutes_réponses"] = answers
                    self.questions_llm.append(true_dict)
                except:
                    self.num_questions -= 1
                generated_text = ""
        return generated_text

        
    # Displays the quiz interface
    def display_question(self, index):
        if index >= self.num_questions:
            self.finish_quiz()
            return
            
        with self.out:
            clear_output(wait=True)
            if len(self.questions_llm) <= index:
                display(HTML("<h4>⏳ Chargement de la question, veuillez patienter...</h4>"))
                while(len(self.questions_llm) <= index):
                    if(self.num_questions <= 0):
                        display(HTML("<h4>❌ La génération du quiz a échoué. Veuillez relancer cette cellule.</h4>"))
                        return
                    elif index >= self.num_questions:
                        self.finish_quiz()
                        return
            question = self.questions_llm[index]["énoncé"]
            right_answer = self.questions_llm[index]["bonne_réponse"]
            answers = self.questions_llm[index]["toutes_réponses"]
            clear_output(wait=True)
            display(Markdown(f"<h4>Question {index+1}/{self.num_questions}: {question}</h4>"))
            
            radio_buttons = widgets.RadioButtons(
                options=answers,
                value=self.selected_answers[index],  # Selected value
                description="Choisissez l'option correcte:",
                disabled=False,
                layout={'width': 'max-content'},
            )
    
            display(radio_buttons)
    
            if index > 0:
                button_back = widgets.Button(description='Précédent', disabled=False)
            else:
                button_back = widgets.Button(description='Précédent', disabled=True)
            button_back.style.button_color = 'lightblue'
            if index < (self.num_questions - 1):
                button_next = widgets.Button(description='Suivant')
            else:
                button_next = widgets.Button(description='Finaliser')
            button_next.style.button_color = 'lightgreen'  

            print("\n")
            button_box = widgets.HBox([button_back, button_next])
            display(button_box)
            
            def on_button_back_click(b):
                self.selected_answers[index] = radio_buttons.value
                self.display_question(index - 1)
    
            def on_button_next_click(b):
                self.selected_answers[index] = radio_buttons.value
                self.display_question(index + 1)
    
    
            button_back.on_click(on_button_back_click)
            button_next.on_click(on_button_next_click)
    
    # Function to finish quiz and show results
    def finish_quiz(self):
        final_answers = self.questions_llm.copy()
        number_correct = 0
        with self.out:
            clear_output(wait=True)
            display(HTML("<h2>Quiz terminé !</h2>"))
            for i in range(len(final_answers)):
                final_answers[i]["réponse_sélectionnée"] = self.selected_answers[i]
                if final_answers[i]["réponse_sélectionnée"] == final_answers[i]["bonne_réponse"]:
                    number_correct += 1
                    display(HTML(f"<h4>✔️ Question {i+1}: {final_answers[i]['énoncé']}</h4>"))
                    display(Markdown(f"**Réponse Sélectionnée :** {final_answers[i]['réponse_sélectionnée']}"))
                    print("\n")
                else:
                    display(HTML(f"<h4>❌ Question {i+1}: {final_answers[i]['énoncé']}</h4>"))
                    display(Markdown(f"**Réponse Sélectionnée :** {final_answers[i]['réponse_sélectionnée']}"))
                    display(Markdown(f"**Réponse Correcte :** {final_answers[i]['bonne_réponse']}"))
                    print("\n")
            display(HTML(f"<h4>📜 Votre nombre de réponses correctes est de {number_correct}/{self.num_questions}.</h4>"))
            print("\n")
            button_feedback = widgets.Button(description='Feedback')
            button_feedback.style.button_color = 'lightgreen' 
            display(button_feedback)
            def on_button_feedback_click(b):
                self.out.clear_output()
                with self.out:
                    prompt_feedback = f"Générez un feedback pour un étudiant à partir des réponses qu'il a données à un quiz de type QCM. Organisez votre feedback en rappelant toujours les questions et les réponses lorsque l'étudiant n'a plus accès au quiz, en expliquant pourquoi la bonne alternative est correcte et pourquoi les mauvaises alternatives sont incorrectes. Si l'élève a choisi l'alternative incorrecte, renforcez votre explication sur la source possible de la confusion qui l'a conduit à se tromper dans la question et soulignez, parmi les alternatives disponibles, celle qui est correcte. Récapitulatif du quiz : {final_answers}"
                    chunks = "# 📚 Feedback sur le quiz : \n\n"
                    if self.model_name == "aristote/llama" or self.model_name == "aristote/mixtral":
                        generated_text = self.aristote_generate(prompt_feedback, chunks)
                    else:
                        messages = [{"role": "user", "content": prompt_feedback}]
                        generated_text = self.huggingface_generate(messages, chunks)
            
            button_feedback.on_click(on_button_feedback_click)



    # Config the magic commands and display initial message
    def setup_magics(self):
        self.ip = get_ipython()
        if self.ip:
            self.ip.register_magic_function(self.ai_question, 'line_cell', 'ai_question')
            self.ip.register_magic_function(self.ai_code, 'line_cell', 'ai_code')
            self.ip.register_magic_function(self.ai_quiz, 'line', 'ai_quiz')
            self.ip.register_magic_function(self.ai_explain, 'line_cell', 'ai_explain')
            self.ip.register_magic_function(self.ai_debug, 'line_cell', 'ai_debug')
            self.ip.register_magic_function(self.ai_help, 'line', 'ai_help')
            clear_output(wait=True)
            display(Markdown("**UPSay AI Magic Commands** chargé avec succès ✅"))
            display(Markdown("Cette boîte à outils est expérimentale et en phase de test. Elle peut donc présenter des anomalies."))
            display(Markdown("Utilisez `%ai_help` pour accéder au Guide d'Utilisation."))

    # %ai_question magic command
    def ai_question(self, line="", cell=""):
        question = line + cell
        rag = self.get_context(question)
        rag_prompt = f" Voici un extrait du support de cours qui pourra vous être utile dans votre réponse à l'étudiant: {rag}"
        # Append the users's current question to the messages history
        self.messages_history.append({"role": "user", "content": question})
        # The messages history does not include the RAG results for every exchange. Only the RAG of the current question is present in the messages passed to the LLM
        if self.model_name == "aristote/mixtral":
            messages = [{"role": "user", "content": self.persona_prompt_qa + rag_prompt}, {"role": "assistant", "content": "Bien sûr, je serais ravi de vous aider avec vos questions sur la programmation et la science des données."}] + [x for x in self.messages_history]
        else:
            messages = [{"role": "system", "content": self.persona_prompt_qa + rag_prompt}] + [x for x in self.messages_history]
        initial_response = ""
        clear_output(wait=True)
        self.display_output = display(Markdown(initial_response), display_id=True)
        # Generate answer and display it word by word as it is written (similar to ChatGPT user experience)
        if self.model_name == "aristote/llama" or self.model_name == "aristote/mixtral":
            generated_text = self.aristote_generate(messages, initial_response)
        elif self.model_name == "huggingface/llama":
            generated_text = self.huggingface_generate(messages, initial_response)


        # Append the assistant's answer to the messages history
        self.messages_history.append({"role": "assistant", "content": generated_text})
        # Use the assistant's answer alongside the question to find possible recommendations for the student 
        recommendation = self.get_recommendation(question + " " + generated_text)
        if(recommendation):
            generated_text += "\n\n"
            recommendation_string = "💡 Pour plus d'informations sur ce sujet, il peut être utile de cliquer sur les liens pour réviser les cours :"
            # Also display the recommendation word by word to improve user experience (seamlessly integration with LLM answer)
            for word in recommendation_string.split():
                generated_text += word + ' '
                #display(Markdown(generated_text), clear = True)
                update_display(Markdown(generated_text), display_id=self.display_output.display_id)
                time.sleep(0.05)
            generated_text += recommendation
            #update_display(Markdown(f"{generated_text}{recommendation}."), display_id=self.display_output.display_id)
            update_display(Markdown(generated_text), display_id=self.display_output.display_id)
        
        warning_ia = "\n\n⚠️ Réponse générée par une intelligence artificielle, les informations peuvent ne pas être exactes."
        generated_text += warning_ia
        update_display(Markdown(generated_text), display_id=self.display_output.display_id)
            
        # Limit history length to 10 exchanges user-assistant (i.e. max = 20 messages). If it passes this limit, delete first (oldest) exchange.
        if(len(self.messages_history)>20):
            self.messages_history.pop(0)
            self.messages_history.pop(0)

    # %ai_code magic command
    def ai_code(self, line="", cell=""):
        code_inst = line
        if cell != "":
            code_inst += "\n" + cell
        # No RAG for now
        if self.model_name == "aristote/mixtral":
            messages = [{"role": "user", "content": self.persona_prompt_code}, {"role": "assistant", "content": "Bien sûr, je serais ravi de vous aider avec vos codes python."},  {"role": "user", "content": code_inst}]
        else:
            messages = [{"role": "system", "content": self.persona_prompt_code}, {"role": "user", "content": code_inst}]
        initial_response = "⏳ Une fois la réponse complétée, le code sera déplacé dans une nouvelle cellule juste en dessous.\n\n"
        clear_output(wait=True)
        self.display_output = display(Markdown(initial_response), display_id=True)
        
        if self.model_name == "aristote/llama" or self.model_name == "aristote/mixtral":
            generated_text = self.aristote_generate(messages, initial_response)
        elif self.model_name == "huggingface/llama":
            generated_text = self.huggingface_generate(messages, initial_response)

        generated_text = generated_text.replace(initial_response, "")
        # Chech for the code block inside of the generated answer
        if '```python' in generated_text and '```\n' in generated_text:
            code_init = generated_text.find('```python') + len('```python')
            code_end = generated_text.find('```\n')
            # Put a comment before
            if(cell == ""):
                code = "# ⚠️ Code généré par une intelligence artificielle sujet à des erreurs\n" + f"# Instructions pour la génération : '{code_inst}'\n" + generated_text[code_init:code_end]
            else:
                code = "# ⚠️ Code généré par une intelligence artificielle sujet à des erreurs\n" + f"'''\nInstructions pour la génération : \n{code_inst}'''\n" + generated_text[code_init:code_end]
            code_remove = generated_text[(code_init - len('```python')):(code_end + len('```\n'))]
            generated_text = generated_text.replace(code_remove, "")
            generated_text += "\n\n" + "Le code généré par l'IA a été inséré dans la cellule ci-dessous ⬇️"
            self.ip.set_next_input(code) # Generate new cell with code
        display(Markdown(generated_text), clear = True)



    # %ai_question magic command
    def ai_quiz(self, line=""):
        self.selected_answers = [None, None, None, None, None]
        self.num_questions = self.num_questions_quiz
        self.cours_content = self.get_quiz_context(line.strip())
        clear_output(wait=True)
        if(self.cours_content == None):
            display(HTML("<h5>⚠️ Je n'ai pas pu trouver de liens entre le sujet saisi et le matériel de cours. Essayez de reformuler le sujet ou de demander un quiz sur un autre thème.</h5>"))
        elif(self.cours_content == "error_rag"):
            display(HTML("<h5>⚠️ Pour générer un quiz sur un sujet spécifique, utilisez rag_model = 'dpr'.</h5>"))
        else:
            #content_prompt = f"Cours à utiliser pour générer le quiz : {cours_content}"
            if(self.quiz_subject != ""):
                instructions_prompt = f"Générez {self.num_questions_quiz} questions en français style QCM de niveau de difficulté {self.quiz_difficulty} (niveau {self.quiz_level} à l'université) sur le cours de {self.quiz_subject} donné. Basez vos questions principalement sur les contenus liés à {self.quiz_subject} couverts par le cours susceptibles d'être abordés lors d'examens futurs. N'hésitez pas à poser des questions sur {self.quiz_subject} concernant des détails qui n'apparaissent pas explicitement dans le cours mais que l'étudiant devrait connaître, à condition qu'elles soient pertinentes et au même niveau de difficulté." + " N'oubliez pas de bien séparer les éléments des dictionnaires et de la liste par des virgules conformément aux instructions données et aux standards python." + f" Ne retournez rien d'autre que la liste des dictionnaires python dans le bon format avec les questions QCM en français sur le sujet {self.quiz_subject}."
            else:
                instructions_prompt = f"Générez {self.num_questions_quiz} questions en français style QCM de niveau de difficulté {self.quiz_difficulty} (niveau {self.quiz_level} à l'université) sur le cours donné." + " Basez vos questions principalement sur les contenus liés à l'Introduction à la Science des Données (statistiques, probabilités, mathématiques, programmation python, apprentissage statistique, etc) couverts par le cours susceptibles d'être abordés lors d'examens futurs. N'hésitez pas à poser des questions sur le même sujet concernant des détails qui n'apparaissent pas explicitement dans le cours mais que l'étudiant devrait connaître, à condition qu'elles soient pertinentes et au même niveau de difficulté. N'oubliez pas de bien séparer les éléments des dictionnaires et de la liste par des virgules conformément aux instructions données et aux standards python. Ne retournez rien d'autre que la liste des dictionnaires python dans le bon format avec les questions QCM en français sur le cours donné."
            
            if self.model_name == "aristote/mixtral":
                self.quiz_messages = [{"role": "user", "content": self.persona_prompt_quiz}, {"role": "assistant", "content": "Bien sûr, je générerai le quiz sur le cours donné !"}, {"role": "user", "content": instructions_prompt}]
            else:
                self.quiz_messages = [{"role": "system", "content": self.persona_prompt_quiz}, {"role": "user", "content": instructions_prompt}]
            
            self.questions_llm = []
            # Generate answer and display it word by word as it is written (similar to ChatGPT user experience)
            if self.model_name == "aristote/llama" or self.model_name == "aristote/mixtral":
                Thread(target=self.generate_quiz_questions_aristote).start()
                
            elif self.model_name == "huggingface/llama":
                #raise ValueError("The %ai_quiz command is currently only available for aristote models.")
                clear_output(wait=True)
                display(HTML("<h4>⏳ Chargement des questions, veuillez patienter...</h4>"))
                display(HTML("<h5>Les modèles Hugging Face ne permettent pas encore d'afficher les questions dès qu'elles sont prêtes, il faut donc attendre que toutes les questions soient générées.</h5>"))
                generated_text = self.generate_quiz_questions_huggingface()
                clear_output(wait=True)
                
            self.display_output = display(Markdown(""), display_id=True)
            self.out = widgets.Output()
            display(self.out)
            # Start the interactive loop
            self.display_question(0)



    def ai_explain(self, line="", cell=""):
        initial_response = ""
        try:
            # For the "%ai_explain XX" format
            number_cell = int(line.strip())
            cell_content = self.ip.user_ns['In'][number_cell]
            # Since {} are seen as placeholders in f-strings and cause errors, we change them for {{}}
            clean_cell = cell_content.replace('{', '{{').replace('}', '}}')
        except:
            # For when the user puts the command on the first line of the code cell itself
            # Since {} are seen as placeholders in f-strings and cause errors, we change them for {{}}
            clean_cell = cell.replace('{', '{{').replace('}', '}}')
            
            initial_response = "⚠️ Note : Afin d'exécuter le contenu de cette cellule plutôt que d'en générer une explication, vous devez supprimer la commande magique `%%ai_explain` sur la première ligne et exécuter cette cellule à nouveau.\n\n"
            
        if self.model_name == "aristote/mixtral":
            messages = [{"role": "user", "content": self.persona_prompt_explain}, {"role": "assistant", "content": "Bien sûr, je générerai une explication sur le code donné !"}, {"role": "user", "content": clean_cell}]
        else:
            messages = [{"role": "system", "content": self.persona_prompt_explain}, {"role": "user", "content": clean_cell}]
            
        clear_output(wait=True)
        self.display_output = display(Markdown(initial_response), display_id=True)
        
        if self.model_name == "aristote/llama" or self.model_name == "aristote/mixtral":
            generated_text = self.aristote_generate(messages, initial_response)
        elif self.model_name == "huggingface/llama":
            generated_text = self.huggingface_generate(messages, initial_response)


    def ai_debug(self, line="", cell=""):
        initial_response = ""
        try:
            # For the "%ai_explain XX" format
            number_cell = int(line.strip())
            cell_content = self.ip.user_ns['In'][number_cell]
            # Since {} are seen as placeholders in f-strings and cause errors, we change them for {{}}
            clean_cell = cell_content.replace('{', '{{').replace('}', '}}')
            cell_out = self.ip.run_cell(self.ip.user_ns['In'][number_cell])
            clear_output(wait=True)
            if not cell_out.success:
                error_message = f"error_before_exec='{cell_out.error_before_exec}', error_in_exec='{cell_out.error_in_exec}'"
            else:
                display(HTML(f"<h4>✅ Le code fourni ne présente aucun message d'erreur !</h4>"))
                display(Markdown(f"Si vous avez des doutes sur la logique utilisée dans le code ou sur les résultats générés, vous pouvez utiliser la commande `%%ai_question` pour poser des questions spécifiques."))
        except:
            # For when the user puts the command on the first line of the code cell itself
            # Since {} are seen as placeholders in f-strings and cause errors, we change them for {{}}
            clean_cell = cell.replace('{', '{{').replace('}', '}}')
            cell_out = self.ip.run_cell(cell)
            clear_output(wait=True)
            if not cell_out.success:
                error_message = f"error_before_exec='{cell_out.error_before_exec}', error_in_exec='{cell_out.error_in_exec}'"
                initial_response = "⚠️ Note : Après avoir corrigé le bug, afin de bien exécuter le contenu de cette cellule plutôt que d'en générer un rapport de débogage, vous devez supprimer la commande magique `%%ai_debug` sur la première ligne.\n\n"
            else:
                display(HTML(f"<h4>✅ Le code fourni ne présente aucun message d'erreur !</h4>"))
                display(Markdown(f"Si vous avez des doutes sur la logique utilisée dans le code ou sur les résultats générés, vous pouvez utiliser la commande `%%ai_question` pour poser des questions spécifiques."))
                display(Markdown(f"Pour bien exécuter le contenu de cette cellule, vous devez supprimer la commande magique `%%ai_debug` sur la première ligne."))
                
        if not cell_out.success:
            if self.model_name == "aristote/mixtral":
                messages = [{"role": "user", "content": self.persona_prompt_debug}, {"role": "assistant", "content": "Bien sûr, je générerai un un rapport de débogage sur le code donné !"}, {"role": "user", "content": f"Code:\n{clean_cell}\nMessage d'erreur:\n{error_message}"}]
            else:
                messages = [{"role": "system", "content": self.persona_prompt_debug}, {"role": "user", "content": f"Code:\n{clean_cell}\nMessage d'erreur:\n{error_message}"}]
                
            clear_output(wait=True)
            self.display_output = display(Markdown(initial_response), display_id=True)
            
            if self.model_name == "aristote/llama" or self.model_name == "aristote/mixtral":
                generated_text = self.aristote_generate(messages, initial_response)
            elif self.model_name == "huggingface/llama":
                generated_text = self.huggingface_generate(messages, initial_response)
    
    
    # %ai_help magic command
    def ai_help(self, line):
        display(HTML("<h2>Guide d'Utilisation</h2>"))
        display(Markdown("L'**UPSay AI Magic Commands** est un ensemble d'outils expérimentaux d'IA Générative inspiré de jupyter-ai et actuellement en cours de développement à l'Université Paris-Saclay."))
        display(Markdown("<h4>Liste des Commandes Magiques :</h4>"))
        display(HTML("<hr>"))
        display(HTML("<h4><strong><code>%ai_question</code></strong></h4>"))
        display(Markdown("**Description :** Commande magique conçue pour les questions/réponses (Q&R)."))
        display(Markdown("**Mode d'emploi :** Placez la commande dans la première ligne d'une cellule, suivie d'une question sur la même ligne. La réponse apparaîtra au format Markdown juste en dessous de la cellule."))
        display(Markdown("**Exemple d'utilisation :**"))
        display(Markdown(f"<span style='color: gray;'>[ 42 ] : </span>`%ai_question Quelle est la différence entre causalité et corrélation ?{' '.join([' ' for i in range(200)])}`"))
        display(Markdown("**Note :** Vous pouvez utiliser **`%%ai_question`** (double %) si vous préférez utiliser plusieurs lignes pour formuler votre question."))
        display(HTML("<hr>"))
        display(HTML("<h4><strong><code>%ai_code</code></strong></h4>"))
        display(Markdown("**Description :** Commande magique conçue pour la génération de code (python)."))
        display(Markdown("**Mode d'emploi :** Placez la commande dans la première ligne d'une cellule, suivie des instructions pour la génération du code sur la même ligne. Le code généré apparaîtra dans une nouvelle cellule."))
        display(Markdown("**Exemple d'utilisation :**"))
        display(Markdown(f"<span style='color: gray;'>[ 42 ] : </span>`%ai_code Fonction qui calcule le déterminant d'une matrice numpy.{' '.join([' ' for i in range(200)])}`"))
        display(Markdown("**Note :** Vous pouvez utiliser **`%%ai_code`** (double %) si vous préférez utiliser plusieurs lignes pour formuler vos intructions de code."))
        display(HTML("<hr>"))
        display(HTML("<h4><strong><code>%ai_explain</code></strong></h4>"))
        display(Markdown("**Description :** Commande magique conçue pour les explications de code."))
        display(Markdown("**Mode d'emploi :** Il existe deux manières d'utiliser cette commande :"))
        display(Markdown("• Placez la commande `%ai_explain` dans la première ligne d'une cellule, suivie sur la même ligne du numéro de la cellule où se trouve le code à expliquer (il faut qu'elle ait été exécutée dans la session en cours)."))
        display(Markdown("• Placez la commande `%%ai_explain` (double %) dans la première ligne de la cellule où se trouve le code à expliquer. Le code de la cellule ne sera pas exécuté, seule son explication sera générée."))
        display(Markdown("**Exemple d'utilisation :** (Supposons que le code à expliquer ait été exécuté dans la cellule [ 21 ] pendant la session en cours)"))
        display(Markdown(f"<span style='color: gray;'>[ 42 ] : </span>`%ai_explain 21{' '.join([' ' for i in range(200)])}`"))
        display(HTML("<hr>"))
        display(HTML("<h4><strong><code>%ai_debug</code></strong></h4>"))
        display(Markdown("**Description :** Commande magique conçue pour le débogage de code."))
        display(Markdown("**Mode d'emploi :** Il existe deux manières d'utiliser cette commande :"))
        display(Markdown("• Placez la commande `%ai_debug` dans la première ligne d'une cellule, suivie sur la même ligne du numéro de la cellule où se trouve le code à déboguer (il faut qu'elle ait été exécutée dans la session en cours)."))
        display(Markdown("• Placez la commande `%%ai_debug` (double %) dans la première ligne de la cellule où se trouve le code à déboguer. Le code de la cellule ne sera pas exécuté, seule son analyse de débogage sera générée."))
        display(Markdown("**Exemple d'utilisation :** (Supposons que le code à déboguer ait été exécuté dans la cellule [ 21 ] pendant la session en cours)"))
        display(Markdown(f"<span style='color: gray;'>[ 42 ] : </span>`%ai_debug 21{' '.join([' ' for i in range(200)])}`"))
        display(Markdown("**Note :** Uniquement pour les codes qui présentent un message d'erreur lorsqu'ils sont exécutés. Pour les codes qui s'exécutent mais génèrent des résultats inattendus, vous pouvez utiliser la commande `%%ai_question` pour poser des questions spécifiques."))
        display(HTML("<hr>"))
        display(HTML("<h4><strong><code>%ai_quiz</code></strong></h4>"))
        display(Markdown("**Description :** Commande magique conçue pour la génération de quiz style QCM."))
        display(Markdown("**Mode d'emploi :** Il existe trois manières d'utiliser cette commande, en fonction du sujet du quiz que vous souhaitez obtenir :"))
        display(Markdown("• Placez la commande toute seule dans la première ligne d'une cellule vide : pour générer un quiz sur une leçon (notebook du cours) aléatoire."))
        display(Markdown("• Placez la commande dans la première ligne d'une cellule, suivie du sujet souhaité pour le quiz sur la même ligne : pour générer un quiz sur un sujet spécifique."))
        display(Markdown("• Placez la commande dans la première ligne d'une cellule, suivie du nom d'une leçon (notebook du cours) au format CMx ou CMx.md sur la même ligne : pour générer un quiz sur une leçon spécifique."))
        display(Markdown("**Exemples d'utilisation :**"))
        display(Markdown(f"<span style='color: gray;'>[ 42 ] : </span>`%ai_quiz{' '.join([' ' for i in range(200)])}`"))
        display(Markdown(f"<span style='color: gray;'>[ 42 ] : </span>`%ai_quiz réseau de neurones{' '.join([' ' for i in range(200)])}`"))
        display(Markdown(f"<span style='color: gray;'>[ 42 ] : </span>`%ai_quiz CM4{' '.join([' ' for i in range(200)])}`"))
        display(HTML("<hr>"))
        
