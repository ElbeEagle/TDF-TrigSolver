

# MultiMath: Bridging Visual and Mathematical Reasoning for Large Language Models


# Abstract

The rapid development of large language models (LLMs) has spurred extensive research into their domain-specific capabilities, particularly mathematical reasoning. However, most open-source LLMs focus solely on mathematical reasoning, neglecting the integration with visual injection, despite the fact that many mathematical tasks rely on visual inputs such as geometric diagrams, charts, and function plots. To fill this gap, we introduce MultiMath-7B, a multimodal large language model that bridges the gap between math and vision. MultiMath-7B is trained through a four-stage process, focusing on vision-language alignment, visual and math instruction-tuning, and process-supervised reinforcement learning. We also construct a novel, diverse and comprehensive multimodal mathematical dataset, MultiMath-300K, which spans K-12 levels with image captions and step-wise solutions. MultiMath-7B achieves state-of-the-art (SOTA) performance among open-source models on existing multimodal mathematical benchmarks and also excels on text-only mathematical benchmarks. Our model and dataset are available at https://github.com/pengshuai-rin/MultiMath.

# Introduction

The rapid development of large language models (LLMs) has ushered in significant advancements in various domains, with a focus on specialized capabilities, particularly mathematical reasoning. Many domain-specific language models have primarily concentrated on mathematical reasoning in isolation (Yu et al. 2024; Luo et al. 2023; Wang et al. 2024; Shao et al. 2024), while neglecting the integration with visual reasoning. Simultaneously, general-purpose open-source multimodal large language models (MLLMs) (Liu et al. 2023b; Zhu et al. 2024) often lack specificity in vertical domains, resulting in a subpar performance in mathematical reasoning tasks.

Currently, domain-specific MLLMs for mathematical reasoning can be categorized into two types. The first, represented by G-LLaVA (Gao et al. 2023) and AlphaGeometry (Trinh et al. 2024), focuses on geometric problem solving (GPS) (Seo et al. 2015; Sachan and Xing 2017; Lu et al. 2021; Peng et al. 2023) but falls short in other multimodal mathematical reasoning tasks, such as function plot reasoning and scientific chart QA (Lu et al. 2024). The second, represented by Math-LLaVA (Shi et al. 2024), builds upon an existing open-source MLLM with math finetuning. However, it underperforms in text-only mathematical reasoning tasks (Cobbe et al. 2021; Hendrycks et al. 2021; Wei et al. 2023) due to the lack of large-scale pretraining on math corpora and the absence of chain-of-thought (CoT) reasoning capabilities. Consequently, there remains a notable gap in the availability of an open-source MLLM that excels across a broad spectrum of mathematical reasoning tasks.

<div style="display: block; width: 100%"><img src="https://storage.simpletex.cn/view/m50ded27bd67f2da92c81d15d6139a729" style="width: 39%; max-width: 39%" /></div> Figure 1: Comparison between MultiMath-7B and existing open-source MLLMs and Math LLMs across various math benchmarks and math skills. The data in the figure has been normalized.

To bridge this gap, we introduce MultiMath-7B, a domain-specific multimodal large language model for mathematical reasoning. Unlike Math-LLaVA (Shi et al. 2024), which directly applies math finetuning to existing MLLMs, we choose to build upon a well-trained math LLM as our foundation. We then enhance it with visual capabilities and align its visual and mathematical reasoning. This strategy leverages the reasoning abilities acquired from mathematical pretraining and extends them to the visual domain. MultiMath-7B employs DeepSeekMathRL-7B (Shao et al. 2024) as the foundation language model, augmented with a vision encoder and a multimodal adapter to enable visual capabilities. We adopt a multi-stage training process, progressively training the model's visual alignment, visual dialogue, and visual reasoning abilities, ultimately bridging them with mathematical reasoning skills.

Another challenge in developing a math MLLM is the scarcity of multimodal alignment and instruction datasets in math domain. Existing open-source datasets typically focus on particular math subfields and lack visual-language alignment data and CoT-style instruction data. To address it, we construct MultiMath-300K, a multimodal, multilingual, multi-level and multistep mathematical reasoning dataset that encompasses a wide range of K-12 level mathematical problems. MultiMath-300K demonstrates three key strengths over existing multimodal math datasets Geo170K (Gao et al. 2023) and MathV360K (Shi et al. 2024): Novelty: the problems are not present in previously released datasets.

Diversity: MultiMath-300K covers almost all K-12 grades, including a variety of math problem types such as arithmetic, algebra, geometry, function, algorithm, etc. Comprehensiveness: each problem is accompanied by an image caption for vision-language alignment training and a step-by-step solution for CoT instruction fine-tuning. The comparison of MultiMath-300K with Geo170K and MathV360K is shown in Table 1.

Experimental results on mathematical reasoning tasks demonstrate that MultiMath-7B not only achieves SOTA performance among open-source models on multimodal mathematical benchmarks but also excels on text-only mathematical benchmarks. Notably, multimodal training has been shown to improve the model's performance on certain text-only mathematical reasoning tasks, suggesting that incorporating multimodal reasoning can enhance the language model's overall reasoning abilities.

The main contributions are summarized as follows:

We propose MultiMath-7B, a math MLLM that achieves SOTA performance among open-source models on multi-modal mathematical benchmarks and excels in text-only mathematical reasoning tasks.

We constructed MultiMath-300K, a multimodal, multilingual, multi-level and multistep mathematical reasoning alignment and instruction dataset, covering a wide range of K-12 level mathematical problems.

We introduce a training framework for enhancing the multimodal capabilities of domain-specific models, preserving the original abilities while boosting multimodal performance.

# Related Work

# Multimodal Large Language Model

Table 1: Comparison with existing multimodal math reasoning datasets Geo170K and MathV360K.

| Dataset | Original | Task | Data | CoT |
| --- | --- | --- | --- | --- |
| GPS | MWP | FQA | Align | QA |
| Geo170K |  | ✓ |  |  | ✓ | ✓ |
| MathV360K |  | ✓ | ✓ | ✓ | ✓ | ✓ |
| MultiMath-300K | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

Recent advancements in vision-language alignment and the maturation of large language model (LLM) have endowed LLMs with visual capabilities. Pioneering studies in vision-language alignment include CLIP (Radford et al. 2021) and BLIP (Li et al. 2022). CLIP aligns image and text semantic spaces through contrastive learning, while BLIP enhances visual-language understanding and generation by jointly training a vision encoder with a language model. Inspired by these models, researchers developed MLLMs such as Mini-GPT4 (Zhu et al. 2024) and LLaVA (Liu et al. 2023b), which leverage vision-language alignment training and instruction-tuning to enable LLMs to handle multimodal tasks. Recently, closed-source MLLMs like GPT-4V (OpenAI 2024),

Gemini Pro (Gemini 2024), and Claude 3 (Anthropic 2024) have further pushed the boundaries of visual understanding capabilities. The typical training framework involves using pretrained vision encoders and language models, aligning them with visual caption data, and finally finetuning on instruction data for task-specific abilities.

Despite these advancements, there is still a significant gap in the development of domain-specific MLLMs, particularly in mathematical reasoning. This gap is due to the lack of an effective training framework for adapting math LLMs to multimodalities and the scarcity of multimodal alignment and instruction reasoning data. In this paper, we aim to address these issues.

# Mathematical Reasoning

Automated mathematical reasoning is a significant research area in artificial intelligence. It typically includes tasks such as mathematical word problems (MWP) (Wang et al. 2018), geometry problem solving (GPS) (Lu et al. 2021), and automatic theorem proving (ATP) (Chou, Gao, and Zhang 1996). The emergence of large language models (LLMs) has led to their dominance in numerous mathematical reasoning benchmarks, driven by their extensive pretraining and advanced comprehension and reasoning capabilities. Mathematical reasoning has increasingly garnered attention from researchers and has become an essential benchmark for assessing LLMs. Several specialized LLMs, such as MetaMath (Yu et al. 2024), Math-Shepherd (Wang et al. 2024), WizardMath (Luo et al. 2023), and DeepSeekMath (Shao et al. 2024), have been developed to address these tasks. Derived from general-purpose LLMs, these models are fine-tuned to strengthen their mathematical abilities. Open-source LLMs have shown strong performance on mathematical reasoning benchmarks, highlighting the potential of domain-specific models.

A challenge of mathematical reasoning lies in reasoning with visual injection, including geometry diagrams, scientific charts, function plots, etc. However, existing math MLLMs are either limited to geometric problems, as seen with G-LLaVA (Gao et al. 2023), or underperform in text-only mathematical reasoning tasks and lack chain-of-thought capabilities, such as Math-LLaVA (Shi et al. 2024). To address these issues, we construct a novel, diverse, and comprehensive multimodal math reasoning dataset, including visual-language alignment data and step-by-step reasoning instructions. We use this dataset to train MultiMath-7B, filling the gap in open-source math MLLMs.



<div style="display: block; width: 100%"><img src="https://storage.simpletex.cn/view/m757caed59d40a16945aa67b279b770f2" style="width: 32%; max-width: 32%" /></div> Figure 2: Statistics of MultiMath-300K, where each ring corresponds to an individual statistical dimension.

# Dataset

In this section, we introduce the MultiMath-300K dataset, with a focus on the construction process.

# Overview

MultiMath-300K comprises 298,670 mathematical problems, with 290,227 in the training set and 8,443 in the validation set. Each problem features an image and a statement in both English and Chinese. Covering all K-12 education levels, MultiMath-300K includes knowledge points such as arithmetic, algebra, mathematical concepts, plane geometry, solid geometry, function analysis, and algorithm derivation. Figure 2 illustrates these statistics in a pie chart.

In addition to the problem data, MultiMath-300K includes vision-language alignment data and step-by-step solution instructions. The alignment data details the image for vision-language alignment training. The instruction data provides step-by-step reasoning solutions, with each step featuring an ID, name, and content, culminating in a final answer marked in boxed. Figure 3 presents a data sample of the English part.

# Dataset Construction

Here we outline the dataset construction process, encompassing collection, annotation, and verification, as illustrated on the left side of Figure 4.

Source Data To ensure novelty, we collect mathematical problems from K-12 textbooks, exercises, and exams with authorization from the data providers. Selection criteria include (1) Completeness, requiring each problem to include the question title, details, solution, and standard answer. (2) Multimodality, with each problem featuring exactly one image. (3) Clarity, excluding images that are too small or blurry. This process initially yields 390,000 raw problems. We then use GPT-4-1106-preview to translate the problem texts, resulting in bilingual descriptions in both Chinese and English.

Alignment Data The alignment data serve two purposes: (1) facilitating vision-language alignment training for multimodal models and (2) enabling language models to ad

<div style="display: block; width: 100%"><img src="https://storage.simpletex.cn/view/m10ea1ac6888bb205f9594333021bebe1" style="width: 38%; max-width: 38%" /></div> Figure 3: A data sample from MultiMath-300K, including the statement, image, caption, and solution, all in English. A complete sample also contains the Chinese statement, caption, solution, and other fields.

dress multimodal problems through text-only descriptions. We utilized GPT-4o-2024-05-13 to generate bilingual captions for images in both Chinese and English. To address GPT-4o's limitations in OCR accuracy, we employed Math-Pix $^{1}$ to verify and correct OCR results for formula and textual images.

Instruction Data Chain-of-thought (CoT) (Wei et al. 2022) reasoning has proven effective in enhancing LLM's mathematical reasoning abilities. To effectively utilize CoT reasoning, step-by-step instructional data is essential for model training, as it supports precise tracking of reasoning errors and enables fine-grained tuning. Therefore, our objective is to construct multistep reasoning data. We employed GPT-4o-2024-05-13 and GPT-4-1106-preview for annotation, conducting multiple rounds of refinement to ensure high-quality results, as follows:

Round 1: Generate step-by-step reasoning chains using GPT-4o, with detailed solutions from the original data as the hint.

Round 2: Evaluate GPT-4o's reasoning chains against the standard answers. If inconsistencies are found, require GPT-4o to revise the reasoning steps.



<div style="display: block; width: 100%"><img src="https://storage.simpletex.cn/view/m707d7df091a35b962adc204b4f88776e" style="width: 81%; max-width: 81%" /></div> Figure 4: An illustration of the dataset construction and model training process. We collected problem sets from textbooks, exercises, and exams, and utilized GPT-4o for annotation and verification, producing the MultiMath-300K dataset for model training. The model's training is illustrated on the right, detailing the data types and training modules at each stage.

Round 3: Submit GPT-4o's responses and the standard answers to GPT-4 for verification, and retain only the correct answers.

Following these rounds of refinement, we compiled 300K problems to create MultiMath-300K. For further details on our dataset and the prompts used in its construction, please refer to the Appendix.

# Model Training

# Model Architecture

MultiMath-7B is built upon the LLaVA architecture (Liu et al. 2023a) and integrates three primary components: a vision encoder, a multimodal adapter, and a language model. The vision encoder is initialized with openai/clip-vit-large-patch14-336, which supports a 336×336 image resolution to effectively capture and recognize small text and mathematical symbols. The multimodal adapter is a two-layer MLP, initialized randomly. The language model is based on DeepSeekMath-RL (Shao et al. 2024), a leading open-source 7B model in math reasoning.

# Training Stage

Here we detail the training process of MultiMath-7B, presenting a novel framework for enhancing the multimodal capabilities of domain-specific LLMs. The overview is depicted on the right side of Figure 4. The training is structured into four stages, each addressing distinct aspects: vision-language alignment, visual instruction-tuning, math instruction-tuning, and finally, math process-supervised reinforcement learning. This sequential approach enables the model to extend its mathematical reasoning ability to the visual domain.

Vision-Language Alignment In this stage, we focus on aligning the vision encoder and language model, enabling the latter to integrate visual information, which it has not previously processed. We train only the multimodal adapter while keeping the other modules freezed. Considering the potential lack of expertise of the initial vision encoder in mathematical content, we mix LLaVA-Pretrain (Liu et al. 2023a) dataset with domain-specific data from MultiMath300K alignment data and geo170k-align (Gao et al. 2023). The model is then trained for one epoch to align visual and language features within the mathematical domain.

In this section, we introduce the proposed mathematical multimodal large language model, MultiMath-7B. Compared to existing open-source mathematical MLLMs, our model offers three main advantages: (1) it tackles a broad spectrum of multimodal mathematical reasoning tasks, (2) it utilizes chain-of-thought (CoT) for detailed step-by-step reasoning, and (3) it maintains strong performance in text-only mathematical reasoning tasks. The appendix details the model training settings.

Vision Instruction-tuning This stage aims to enhance the model's visual comprehension and question-answering abilities. Although the model can now interpret visual information after stage 1, it still struggles with various visual tasks. To address this, we train all model components for two epochs using the LLaVA-Instruction (Liu et al. 2023a) dataset, which focuses on improving visual comprehension and question-answering capabilities.



Math Instruction-tuning In this stage, we focus on extending mathematical reasoning capabilities to visual data, emphasizing chain-of-thought (CoT) reasoning. The CoT training is primarily driven by the MultiMath300K-instruction dataset. Additionally, we incorporate two open-source multimodal mathematical QA datasets, Geo170k-qa (Gao et al. 2023) and MathV360k (Shi et al. 2024), to further enhance the model's performance. This combined training, conducted over two epochs, refines all model components and results in the instruction model.

# Experiment Results

Process-supervised Reinforcement Learning This stage aims to correct errors at the step level during reasoning. Unlike supervised fine-tuning (SFT) in stage 2 and 3, reinforcement learning (RL) enhances the model's ability to identify and correct reasoning errors more effectively. We use MultiMath300K-val, GSM8K-train (Cobbe et al. 2021), MATH-train (Hendrycks et al. 2021), and CMATH-train (Wei et al. 2023) for PPO (Schulman et al. 2017) training. The RL training process, illustrated in Figure 5, is summarized as follows:

Given a mathematical problem, the instruction model

performs chain-of-thought (CoT) reasoning and generates a result consisting of multiple reasoning steps.

Given the standard answer and the model output from the previous step, GPT-4o accesses the correctness of the response. If incorrect, it identifies the step where the error occurred and regenerates the correct solution from that step.

The correct and incorrect answers from the previous step form a paired preference dataset, used to train a reward model initialized from the instruction model.

The reward model assigns a reward score to each reasoning step (action) generated by the policy model, supervising the policy model's gradient descent.

This process results in the final RL-enhanced model. We will discuss the performance improvements from reinforcement learning in the Discussion section.

This section evaluates the performance of MultiMath-7B across various mathematical reasoning benchmarks, including visual and textual math reasoning tasks.

# Visual Math Benchmarks

Datasets and Baselines We select two representative multimodal mathematical reasoning datasets for evaluation: MathVista (Lu et al. 2024) and MathVerse (Zhang et al. 2024). MathVista assesses LLM' mathematical reasoning within visual contexts, while MathVerse presents more complex challenges in plane geometry, solid geometry, and functions. For evaluation, we utilize the provided prompts and perform zero-shot inference. Our baselines include closed-source MLLMs, open-source MLLMs, and two open-source MLLMs G-LLaVA (Gao et al. 2023) and Math-LLaVA (Shi et al. 2024).

Main Results Table 2 presents the evaluation results of MathVista and MathVerse on the testmini dataset, including both closed-source and open-source MLLMs. MultiMath-7B sets a new state-of-the-art (SOTA) among open-source models for both benchmarks. Remarkably, despite having only 7B parameters, MultiMath-7B surpasses models with up to 34 billion parameters, demonstrating its exceptional performance in visual-mathematical reasoning tasks. Additionally, MultiMath-7B outperforms the closed-source Qwen-VL-Plus (Bai et al. 2023) on both datasets, with its MathVista performance comparable to GPT-4V.

Subset Results We also report the results on the subsets of MathVista and MathVerse: MathVista is divided into Figure QA, Geometry Problem Solving, Math Word Problem, Textbook QA, and Visual QA. MathVerse is categorized into Text Dominant, Text Lite, Vision Intensive, Vision Dominant, and Vision Only. MultiMath-7B notably excels across most subsets, significantly outperforming other MLLMs in Geometry Problem Solving and Math Word Problem tasks. It also leads open-source MLLMs in most MathVerse subsets, with the exception of the Vision Only category.

<div style="display: block; width: 100%"><img src="https://storage.simpletex.cn/view/m12c8fed50e1bd7555b3096f501e11982" style="width: 38%; max-width: 38%" /></div> Figure 5: An illustration of RL data construction and training. Leveraging step-wise reasoning, GPT-4o identifies and corrects errors, generating preference data for training the reward model, which then guides reinforcement training with step-level rewards for error correction.



| Model | MathVisiona | MathVerse |
| --- | --- | --- |
| ALL | FQA | GPS | MWP | TQA | VQA | ALL | TD | TL | VI | VD | VO |
| Heuristics Baselines |
| Random | 17.9 | 18.2 | 21.6 | 3.8 | 19.6 | 26.3 | 12.4 | 12.4 | 12.4 | 12.4 | 12.4 | 12.4 |
| Human | 60.3 | 59.7 | 48.4 | 73.0 | 63.2 | 55.9 | 64.9 | 71.2 | 70.9 | 41.7 | 68.3 | 66.7 |
| Closed-Source MLLMs |
| GPT-4o (OpenAI 2024) | 63.8 | $-$ | $-$ | $-$ | $-$ | $-$ | $-$ | $-$ | $-$ | $-$ | $-$ | $-$ |
| GPT-4V (OpenAI 2024) | 49.9 | 43.1 | 50.5 | 57.5 | 65.2 | 38.0 | 54.4 | 63.1 | 56.6 | 51.4 | 50.8 | 50.3 |
| Gemini Pro (Gemini 2024) | 63.9 | $-$ | $-$ | $-$ | $-$ | $-$ | 35.3 | 39.8 | 34.7 | 32.0 | 36.8 | 33.3 |
| Claude 3.5 (Anthropic 2024) | 67.7 | $-$ | $-$ | $-$ | $-$ | $-$ | $-$ | $-$ | $-$ | $-$ | $-$ | $-$ |
| Qwen-VL-Plus (Bai et al. 2023) | 43.3 | 54.6 | 35.5 | 31.2 | 48.1 | 51.4 | 21.3 | 26.0 | 21.2 | 18.5 | 19.1 | 21.8 |
| Open-Source MLLMs |
| mPLUG-OwI2-7B (Ye et al. 2024) | 22.2 | 22.7 | 23.6 | 10.2 | 27.2 | 27.9 | 8.3 | 8.9 | 9.1 | 10.2 | 8.1 | 5.3 |
| MiniGPT4-7B (Zhu et al. 2024) | 23.1 | 18.6 | 26.0 | 13.4 | 30.4 | 30.2 | 12.2 | 12.3 | 12.9 | 12.5 | 14.8 | 8.7 |
| LLaVA-1.5-13B (Liu et al. 2023a) | 27.7 | 23.8 | 22.7 | 18.9 | 43.0 | 30.2 | 14.3 | 20.3 | 11.1 | 14.9 | 13.2 | 12.0 |
| SPHINX-V2-13B (Lin et al. 2023) | 36.7 | 54.6 | 16.4 | 23.1 | 41.8 | 43.0 | 16.1 | 20.4 | 14.1 | 14.0 | 15.6 | 16.2 |
| LLaVA-NeXT-34B (Liu et al. 2024) | 46.5 | $-$ | $-$ | $-$ | $-$ | $-$ | 16.6 | 24.8 | 12.0 | 18.2 | 13.9 | 14.1 |
| G-LLaVA-7B (Gao et al. 2023) | 25.1 | 19.1 | 48.7 | 3.6 | 25.0 | 28.7 | 17.8 | 24.9 | 22.1 | 18.0 | 15.2 | 9.0 |
| Math-LLaVA-13B (Shi et al. 2024) | 46.6 | 37.2 | 57.7 | 56.5 | 51.3 | 33.5 | 20.1 | 22.8 | 21.8 | 21.1 | 19.2 | 15.4 |
| MultiMath-7B | 50.0 | 40.1 | 66.8 | 61.8 | 50.0 | 33.0 | 26.9 | 34.8 | 30.8 | 28.1 | 25.9 | 15.0 |Table 2: Comparison with closed-source and open-source MLLMs on the testmini set of MathVista and MathVerse.

# Textual Math Benchmarks

Datasets&Baselines We selected four representative textual mathematical reasoning datasets for evaluation: GSM8K (Cobbe et al, 2021) and MATH (Hendrycks et al, 2021) in English, CMATH (Wei et al, 2023) and Gaokao-MathCloze (Zhong et al, 2023) in Chinese. GSM8K and CMATH focus on elementary math, while MATH and Gaokao-MathCloze cover high school to university-level problems. We used MultiMath's chain-of-thought prompts and zero-shot inference to assess accuracy. For baseline comparisons, we include common closed-source LLMs, open-source foundation LLMs and math LLMs, as well as open-source MLLMs.

# Discussion

Results Table 3 presents the evaluation results on these benchmarks. While closed-source LLMs continue to lead in performance, open-source math LLMs closely follow. MultiMath-7B significantly outperforms 7B and 13B open-source foundation LLMs and MLLMs, but it slightly trails behind the top open-source math LLMs. Notably, despite a decline in text-only reasoning compared to DeepSeekMathRL-7B (Shao et al. 2024), MultiMath-7B excels on the Gaokao-MathCloze dataset. This is attributed to its extensive training on Gaokao-style problems in MultiMath-300K, enhancing the model's capability to solve high school math questions. Additionally, G-LLaVA (Gao et al. 2023) and Math-LLaVA (Shi et al. 2024) underperformed on text-only mathematical tasks, even compared to LLaVA-1.5-7B (Liu et al. 2023a) before its multimodal fine-tuning, indicating that their training is highly specialized for visual mathematical data and less effective for single-modal tasks.

In this section, we explore the factors driving the model's performance, specifically, what contributes to the model's outcomes.

Visual Enhancement or Reasoning Boost? The improvement of mathematical MLLM in multimodal math reasoning tasks compared to its foundation language models can be attributed to two main factors: (1) visual injection, which provides essential context for problem-solving;(2) finetuning on new math reasoning tasks, which boosts the model's reasoning ability in some aspects. To investigate this, we evaluate DeepSeekMathRL-7B on the text-only testmini set of MathVista (Table 4). Converting visual data into text allows the language model to solve multimodal math problems. With the same text-only inputs, MultiMath-7B achieved 9.1 points higher accuracy than DeepSeekMathRL-7B, reflecting gains from reasoning boost alone. Inferring with images further improves the performance by 4.3, indicating gains from visual injection. These findings suggest that while both factors contribute, reasoning boost plays a more substantial role. This supports our assertion that multimodal reasoning training can enhance reasoning abilities within a single modality.

Contribution of Dataset To assess the impact of the proposed MultiMath-300K dataset, we conducted ablation studies by excluding it from pretraining (Stage 1) and math instruction-tuning (Stage 3) and evaluate the models on six mathematical benchmarks (Figure 6). While MathV360K primarily boosted performance on MathVista, it significantly undermined the model's ability on textual math tasks. Incorporating MultiMath-300K during Stage 3 led to substantial improvements across nearly all benchmarks, highlighting its



| Model | English | Chinese |
| --- | --- | --- |
| GSM8K | MATH | CMATH | Gaokao- MathCloze |
| Closed-Source LLMs |
| Gemini Ultra (Gemini 2024) | 94.4 | 53.2 | $-$ | $-$ |
| GPT-4 (OpenAI 2024) | 92.0 | 52.9 | 86.0 | 22.0 |
| GPT-3.5 (Brown et al. 2020) | 80.8 | 34.1 | 73.8 | 7.6 |
| Gemini Pro (Gemini 2024) | 86.5 | 32.6 | $-$ | $-$ |
| Open-Source Foundation LLMs |
| Vicuna-7B (Chiang et al. 2023) | 10.1 | 3.5 | 22.3 | 2.5 |
| Mistral-7B (Jiang et al. 2023) | 40.3 | 14.3 | 44.9 | 5.1 |
| Llemma-7B (Azerbayev et al. 2024) | 37.4 | 18.1 | 43.4 | 11.9 |
| Llama-2-13B (Touvron et al. 2023) | 43.0 | $-$ | $-$ | $-$ |
| Llama-3-8B † (MetaAI 2024) | 79.6 | 30.0 | $-$ | $-$ |
| Llama-3-70B † (MetaAI 2024) | 90.0 | 50.4 | $-$ | $-$ |
| Open-Source Math LLMs |
| WizardMath-7B-v1.1 (Luo et al. 2023) | 83.2 | 33.0 | 66.6 | 6.3 |
| Math-Shepherd-7B (Wang et al. 2024) | 84.1 | 33.0 | 70.1 | 8.5 |
| MetaMath-70B (Yu et al. 2024) | 82.3 | 26.6 | 70.9 | $-$ |
| DeepSeekMath-7B (Shao et al. 2024) | 88.2 | 51.7 | 88.8 | 20.3 |
| Open-Source MLLMs |
| G-LLaVA-7B (Gao et al. 2023) | 2.5 | 1.1 | 11.1 | 0.8 |
| Math-LLaVA-13B (Shi et al. 2024) | 7.4 | 5.9 | 29.0 | 0.0 |
| LLaVA-1.5-7B (Liu et al. 2023a) | 13.4 | 3.5 | 28.4 | 0.0 |
| LLaVA-NeXT-34B (Liu et al. 2024) | 61.5 | 18.3 | 58.4 | 11.9 |
| MultiMath-7B | 79.2 | 46.3 | 84.2 | 28.8 |

Table 3: Results on textual math benchmarks. †: 8-shot for GSM8K and 4-shot for MATH. Table 4: Comparison with DeepSeekMath-7B without multimodal-finetuned and MultiMath-7B on text-only test-mini set of MathVista.

| Model | Settings | MathVista |
| --- | --- | --- |
| DeepSeek Math-RL-7B | text-only | 36.6 |
| MultiMath-7B | text-only | 45.7 |
| MultiMath-7B | with image | 50.0 |

critical role in enhancing comprehensive mathematical reasoning. Additionally, Stage 1's math alignment training provided a modest performance gain.

Contribution of RL Figure 6 also depicts the ablation results of stage 4 math reinforcement Learning. RL improved the model's performance on GSM8K, MATH, CMATH, and MathVista, but led to a decline on MathVerse and Gaokao-MathCloze. This aligns with expectations, as the RL training primarily used in-domain data from GSM8K and MATH, leading to better results on those benchmarks while negatively affecting out-of-domain datasets. This study confirms the viability of step-wise RL for multimodal math training, and future work could explore RL on larger, more diverse datasets to mitigate out-of-domain performance drops.

Contribution of Foundation LM To assess how much of MultiMath-7B's performance attributed to its foundation

<div style="display: block; width: 100%"><img src="https://storage.simpletex.cn/view/md94faf0051a0cf397de0caea17ce9d64" style="width: 30%; max-width: 30%" /></div> Figure 6: Ablation studies of different training stages w/ or w/o MultiMath-300K and RL. The dashed lines denote without stage 3 instruction-tuning.

<div style="display: block; width: 100%"><img src="https://storage.simpletex.cn/view/m17fbed484592e65eee0ab1790bb941f1" style="width: 30%; max-width: 30%" /></div> Figure 7: Performance of different foundation models after MultiMath training.

model, DeepSeekMathRL, we retrained it using Vicuna-7B as a baseline. The results are shown in Figure 7. DeepSeek Math outperforms Vicuna more significantly on textual benchmarks than visual benchmarks. This suggests the gains on visual tasks stem mainly from multimodal training rather than the language model itself. Additionally, compared to Table 3, Vicuna's improvements after MultiMath training support the hypothesis that multimodal reasoning training enhances overall mathematical reasoning abilities.

# Conclusion

In this paper, we introduce MultiMath-7B, a multimodal math large language model that bridges the gap between visual and mathematical reasoning. We also construct a multimodal math dataset MultiMath-300K, which spans K-12 levels and includes image captions and step-wise solutions. MultiMath-7B achieves SOTA performance among open-source models on existing multimodal mathematical benchmarks and also excels on text-only mathematical reasoning datasets. Future work will focus on expanding the model's training with diverse datasets across multiple domains and modalities to overcome its current limitations.


# Appendix

# Dataset

Source and Privacy The math problems in MultiMath-300K are sourced from Xuekubao$^{2}$'s K12 question bank, which is collected from math textbooks, exercises, and exam questions. We purchased usage rights for the question bank and obtained permission for research purposes. During the filtering process, we removed any questions involving students' privacy. We also used an n-gram strategy to compare the data with existing mathematical reasoning datasets and filtered out duplicate questions to ensure the novelty of the dataset.

Prompt We use GPT-4o-2024-05-13 to annotate the image captions and problem solutions. We present the prompts used in the dataset construction, including prompts for the caption (Figure 8), solution (Figure 9), and verification (Figure 10). In these figures, the texts in blue are instructions, and in purple are the input question information. We use these prompts to generate Chinese and English captions and solutions using GPT-4o-2024-05-13 (caption and solution) and GPT-4-1106-preview (verification).

Format We include one thousand data examples of MultiMath-300K in data appendix to demonstrate the data format. The complete dataset has been released on Hugging Face.

# Prompt for Caption

<div style="display: block; width: 100%"><img src="https://storage.simpletex.cn/view/mf75da1e689c18398b8dcf16bda4b35c0" style="width: 37%; max-width: 37%" /></div> Figure 8: Prompt for the caption.

# Prompt for Solution

You are a math expert. You will be given an image extracted from a math problem. Follow the instructions carefully.

Please reason step by step, and put your final answer within \boxed{}$. Each step is placed on a new line, using the following format: Step X (Mathematical theorem/basis used): Detailed solution steps. Answer: \boxed{}.

Answer: \boxed{}

<div style="display: block; width: 100%"><img src="https://storage.simpletex.cn/view/mab73e362c775c3fd5e879ff57c5c07b3" style="width: 38%; max-width: 38%" /></div> Figure 9: Prompt for the solution. Figure 10: Prompt for verification.

# Prompt for Verification

You are a math expert. Follow the instructions carefully.

The question is [TITLE]. Hint: [HINT]. The standard answer is [ANS]. Now there is an answer provided by student is [ANS_TBD].

Please check the answer according to the standard answer. If incorrect, output \boxed{\text{boxed}(Incorrect)}, if correct, output \boxed{\text{boxed}(correct)},



| Stage | Training | Dataset | Samples | Training Module | Epoch | Batchesize per Device | LR | Training Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Vision-Language Alignment | MultiMath-300K-align +Geo170K-align +LLaVA-Pretrain | 1.2M | mm adapter | 1 | 8 | 1e-3 | $$\sim$20h$ |
| 2 | Vision Instruction | LLaVA-Instruction | 665K | vision encoder +mm adapter +language model | 1 | 8 | 2e-5 | $$\sim$9h$ |
| 3 | Math Instruction | MultiMath-300K-instruction +Geo170K-qa +MathV360K | 1.0M | vision encoder +mm adapter +language model | 2 | 8 | 2e-5 | $$\sim$32h$ |
| 4 | Math Reinforcement Learning | MultiMath-300K-val +GSM8K-train +MATH-train +CMATH-dev | 26K | language model | 1 | 32 (rm) 2 (pm) | 5e-7 (rm) 9e-6 (pm) | $$\sim$1h (rm) ~4h (pm)$ |

# Model Training

Here we detail the datasets and settings used on each training stage in Figure 11. All the experiments were conducted on 8 NVIDIA A100-80GB GPUs with the random seed 42. For more implementation details, please refer to our code appendix. The model weights have been released on Hugging Face.

# Model Inference

We inferred our model as well as other MLLMs with the settings of temperature: 0.2, top.p: None, num_beams: 1, max.new_tokens: 1024. We evaluated three times on a task for each model and obtained the average score as the final accuracy.