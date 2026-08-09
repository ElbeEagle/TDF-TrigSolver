

# CMM-Math: A Chinese Multimodal Math Dataset To Evaluate and Enhance the Mathematics Reasoning of Large Multimodal Models


https://github.com/ECNU-ICALK/EduChat-Math

# Abstract

Large language models (LLMs) have obtained promising results in mathematical reasoning, which is a foundational skill for human intelligence. Most previous studies focus on improving or measuring the performance of LLMs based on textual math datasets (e.g., MATH, GSM8K). Recently, a few researchers have released English multimodal math datasets (e.g., MATHVISTA and MATH-V) to evaluate the effectiveness of large multimodal models (LMMs). In this paper, we release a Chinese multimodal math (CMM-Math)

<div style="display: block; width: 100%"><img src="https://storage.simpletex.cn/view/m18f515352a43f696b8c60e4828c7b6b1" style="width: 73%; max-width: 73%" /></div> Figure 1: The performance of large multimodal models (LMMs) across 12 difficulty levels in our CMM-Math, where Level 1 is the easiest and Level 12 is the most difficult.

dataset, including benchmark and training parts, to evaluate and enhance the mathematical reasoning of LMMs. CMM-Math contains over 28,000 high-quality samples, featuring a variety of problem types (e.g., choice, fill-in-the-blank, analysis) with detailed solutions across 12 grade levels from elementary to high school in China. Each problem may contain multiple images, and the visual context may be present in the questions or opinions, which makes this dataset more challenging. Our comprehensive analysis reveals that state-of-the-art LMMs on the CMM-Math dataset face challenges, emphasizing the necessity for further improvements in LMM development. We also propose a Multimodal Mathematical LMM (Math-LMM) to handle the problems with mixed input of multiple images and text segments. The Math-LMM is trained using three stages: foundational pre-training, foundational fine-tuning, and mathematical fine-tuning. The extensive experiments indicate that our model effectively improves math reasoning performance by comparing it with the SOTA LMMs over three multimodal mathematical datasets. Our datasets, codes, and weights will be released on GitHub.


# Keywords

Mathematical Reasoning, Large Multimodal Models, Benchmark, Chinese


# 1 Introduction

The recent advent of large language models (LLMs), like OpenAI's GPT-4 [28] and LLaMA [32], have demonstrated remarkable success across math problem solving, which is an important skill for human intelligence [24]. Several studies utilize chain-of-thought (CoT) [36] to solve the problems step by step [41]. Also, tools and programs are integrated with LLMs to reduce the hallucination problem of math reasoning [12]. LEMMA [2] is a math-specific LLM that is fine-tuned on large-scale mathematical datasets, which obtains great abilities in generating textual solutions for mathematical problems and formulating formal proofs.

Furthermore, to evaluate and improve the mathematical performance of LLMs, some textual math datasets are released [11, 27]. For instance, Hendrycks et al. [16] proposed a MATH dataset that contains 12,500 challenging competition mathematics problems with step-by-step solutions. GSM8K [6] is a dataset of 8.5K high-quality linguistically diverse grade school math word problems. However, these studies mainly focus on textual information while the visual contexts of the problems are not well studied by the previous literature.

Recently, various large multimodal models (LMMs) like GPT-4V [28], LLaVA [23], CogVLM [35] and Gemini [31] are proposed for improving the performance of multimodal reasoning. To measure the mathematic reasoning abilities of LMMs, some researchers released multimodal math benchmarks. MMMU [38] is a popular multimodal dataset that mainly focuses on visual recognition with few problems about simple mathematical reasoning. Additionally, the multimodal datasets designed for mathematical reasoning are also proposed [26, 33]. Lu et al. [26] proposed the first math-specific English benchmark dataset, MATHVISTA, to measure the performance of the LMMs. This dataset includes seven mathematical reasoning types with diverse visual contexts across five primary

tasks. Then, Qiao et al. [29] collected 6.5K visual math problems to explore the problem-solving principles beyond the end-to-end performance. Additionally, Wang et al. [33] organized a math evaluation benchmark, MATH-V, which contains 3,040 mathematical problems across 16 knowledge concepts. These studies mainly focus on measuring the performance of mathematical reasoning for the existing LMMs in English.

Unlike these studies, the unique characteristics of our Chinese Mathematical (CMM-Math) dataset are listed as follows. First, the existing multimodal mathematical datasets are in English, while our CMM-Math focuses on Chinese. Second, we release a benchmark dataset to measure performance and contribute a training dataset to fine-tune LMMs, facilitating future research and increasing accuracy in multimodal mathematical reasoning. Third, our dataset is more complex, with problems that may contain multiple figures in questions or options, as shown in the first example in Figure 2. Moreover, it contains more question types, including choice problems, fill-in-the-blank problems, yes-no problems, and analysis problems. Fourth, our large-scale CMM-Math datasets contain more than 28,000 samples across 12 grade levels from elementary to high school, to ensure the completeness and diversity of the dataset.

We evaluate the state-of-the-art open-source and close-source LMMs on our CMM-Math dataset. The results show that it is a challenge for the current foundation LMMs to handle multimodal mathematical reasoning tasks. Furthermore, we propose a math-specific LMM (Math-LMM) with a mixed instruction to handle the problems with multiple images. We train Math-LMM using three phases: foundational pre-training that aligns visual information with LLM, foundational fine-tuning that captures the abilities of task solving, and mathematical fine-tuning that learns mathematical reasoning. We evaluate the performance of Math-LMM over three benchmark datasets and the results show our model outperforms the open-source LMMs in most cases.

The main contributions of this paper are summarized as follows.

We collect and release a high-quality Chinese multimodal mathematical dataset, CMM-Math, which consists of evaluation and training datasets to measure and improve the performance of the current LMMs.

We propose a math-specific LMM (Math-LMM) that trains with three stages: foundational pre-training, foundational fine-tuning, and mathematical fine-tuning.

We conduct a comprehensive evaluation of the existing LMMs and our Math-LMM model on the CMM-Math dataset. The results show that multimodal mathematical reasoning is still a great challenge for LLMs. Our model outperforms the strong open-source LMMs over CMM-Math, MATHVISTA and Math-V datasets in most cases.

# 2 Related Works

# 2.1 Mathematical Dataset

Various datasets [6, 11, 17, 27] have been introduced to measure the mathematical capabilities of large language models (LLMs). For instance, GSM8K [6] and MATH [17] are two popular textual datasets to comprehensively evaluate the LLMs. These datasets [24] can test the language processing abilities in areas such as mathematical reasoning, computation, and theorem proving, but they do not effectively assess the ability of large multimodal models to solve



<div style="display: block; width: 100%"><img src="https://storage.simpletex.cn/view/mb5bdd0d58ee48db68205eb9b5047259d" style="width: 78%; max-width: 78%" /></div> Figure 2: Some examples in our CMM-Math datasets.

math problems that require visual modalities, such as geometry problems, properties of function graphs, etc.

In the past two years, specialized multimodal datasets for the mathematics domain have emerged to assess the mathematical capabilities of large multimodal models, such as MMMU [38], MATH-VISTA [26], We-Math [29] and MATH-V [33]. MMMU [38] primarily evaluates the model's visual recognition abilities, with only a few questions involving simple mathematical reasoning. MATHVISTA [26] consolidates and transforms existing FQA (Figure Question Answering), GPS (Geometry Problem Solving), MWP (Math Word Problems), TQA (Textbook Question Answering), and VQA(Visual Question Answering) datasets, enabling tests of basic mathematical reasoning, but it covers fewer math concepts and has a limited variety of question types, many of which can be solved with VQA capabilities alone. MATH-V [33] compiles questions from math competitions like Math Kangaroo, UK contests at various levels (Grey, Pink, Junior, Senior), and US competitions (AMC 8, 10, 12) and invitedational events (AIME). This dataset evaluates models across multiple educational levels and topics.

Unlike these datasets, our CMM-Math dataset not only offers evaluations covering multiple grades and topics but also includes both training and evaluation datasets. Furthermore, the problem in our dataset may contain multiple images with detailed solution explanations across a variety of problem types. We have also provided a large amount of Chinese multimodal problems with multiple images across 12 grade levels from elementary to high school.

# 2.2 Large Multimodal Model

With the introduction of GPT-4V [28], many versatile large multimodal models have been proposed. Commonly, these models aim to handle both text and image tasks simultaneously. They employ a tokenizer and a visual encoder (such as CLIP [30]) to encode textual and visual information separately, then concatenate the encoded vectors into a unified input that is fed into the large language model. Notable LLMs include LLaVa [23], Qwen-VL-Max [4], Gemini [31], InternLMX Composer-VL [39], and GPT-4o. These models have greatly succeeded in general multimodal tasks, such as OCR, visual question answering, image captioning, multimodal reasoning, etc. Our CMM-Math aims to provide a detailed and comprehensive evaluation of the mathematical multimodal reasoning

Table 1: Key statistics of CMM-Math.

| Statistic | Number |
| --- | --- |
| Total problems | 28,069 |
| Total images | 15,213 |
| Total detailed solutions | 23,825 |
| Levels | 12 |
| Subjects | 13 |
| Images in questions | 9,490 |
| Images in answers | 5,723 |
| Maximum problem length | 2,016 |
| Minimum problem length | 3 |
| Average problem length | 108.31 |

capabilities of these models. Unlike training methods for general-purpose large multimodal models, we propose a three-stage training method specifically for the mathematical domain.

# 3 Dataset

# 3.1 Dataset Construction

Due to the lack of Chinese multimodal mathematical datasets, we collect and release the CMM-Math dataset, constructed with three main steps: data collection, data cleaning, and data annotation.

During the data collection phase, we gathered over 10,000 real exam papers covering 12 grades of mathematics test problems, from primary school to high school in China. Each exam paper includes various types of questions such as multiple-choice, fill-in-the-blank, and analysis problems. These questions contain both visual and textual information, along with their answers, solutions, grades, and question types. Since the exam papers are in PDF format, we used the Mathpix API$^{1}$ to extract the text and images into markdown format and downloaded the extracted images locally.

During the data cleaning phase, we first convert the problems from the markdown text into a JSON format, including fields such as question type, modality, images, question, options, answer, and solution. Then, we check and correct issues related to text and image recognition, such as text or mathematical formulas that are incorrectly identified as images, and images that are misrecognized.



Table 2: Comparison with existing datasets. EN and CN mean English and China:

|  | Multimodal | Training | Evaluation | Language | #Number | Type |
| --- | --- | --- | --- | --- | --- | --- |
| MATH [17] | X | ✓ | ✓ | EN | 12,500 | Fill-in-the-blank questions |
| GSM8K [6] | X | ✓ | ✓ | EN | 8,500 | Fill-in-the-blank questions |
| MathQA [1] | X | ✓ | ✓ | EN | 37,259 | Fill-in-the-blank questions |
| MMMU [38] | ✓ | X | ✓ | EN | 11,500 | Choice and fill-in-the-blank questions |
| MATHVISTA [26] | ✓ | X | ✓ | EN | 6,141 | Choice and fill-in-the-blank questions |
| We-Math [29] | ✓ | X | ✓ | EN | 6,500 | Choice questions |
| MATH-V [33] | ✓ | X | ✓ | EN | 3,040 | Choice and fill-in-the-blank questions |
| CMM-Math (Ours) | ✓ | ✓ | ✓ | CN | 28,249 | Choice, fill-in-the-blank, yes-no and analysis questions |

Finally, we detect and resolve potential issues within each field, including mismatched question types and overly long parsing.

During the data annotation phase, we ask students to check the problems with the format and context to ensure their quality. Then, we divide the problem into 13 different subjects. Due to the large amount of data and the high cost of manual annotation, we chose three large models, GPT-4o, Gemini, and Qwen-VL-max, to vote on the topics and assign them to the topics based on the principle of minority obeying majority.

# 3.2 Dataset Analysis

Our CMM-Math dataset contains 28,069 problems with rich textual and visual information (See Table 1 and Table 3). It contains 21,200 textual problems and 6,869 multimodal problems, divided into choice, fill-in-the-blank, yes-no, and analysis problems. We also split the data into 12 levels, corresponding to the basic education stage from the first grade of primary school to the third grade of high school, to ensure the dataset's applicability and reference value in educational practice. CMM-Math contains 13 knowledge points, covering most of the mathematical fields encountered in middle and high school, particularly logic, algebra, counting, arithmetic, combinatorics, graph theory, topology, statistics, solid geometry, metric geometry, analytic geometry, descriptive geometry, combinatorial geometry, and transformation geometry.

Our dataset has a more diverse and comprehensive range of question types compared to existing datasets. Particularly, the dataset is finely classified based on three dimensions: grade, subject, and question type. More than 84% of problems have detailed solutions. Following the 1:4 ratio principle, we split the dataset into evaluation and training datasets to measure and enhance the performance of LMMs. The evaluation dataset contains 5,821 examples, and the training dataset contains 22,248 examples.

# 3.3 Comparison with Existing Datasets

To clarify the characteristics of our CMM-Math, we compare it with multiple existing mathematical benchmarks, including textual datasets (e.g., MATH, GSM8K, MathQA) and multimodal datasets (e.g., MMMU, MATHEVISTA, MATH-V, and We-Math), as shown in Table 2. First, most of these datasets are in English while we focus on Chinese to measure LMMs more comprehensively. Second, our CMM-Math is a multimodal dataset for mathematical reasoning, where each problem may contain multiple images, designed for LMMs. Textual MATH and GSM8K datasets are used to evaluate the performance of LLMs. Third, our dataset contains the evaluation and training datasets. The existing multimodal datasets evaluate

Table 3: Detailed statistics of CMM-Math datasets.

| Statistic | #Evaluation | #Training | #Total |
| --- | --- | --- | --- |
| Total problems | 5,821 | 22,248 | 28,069 |
| Total images | 3,794 | 11,419 | 15,213 |
| Total detailed solutions | 5,204 | 18,621 | 23,825 |
| Images in questions |
| Image in answers | 2,144(56.51%) | 7,346(64.33%) | 9,490(62.38%) |
| Images in answers | 1,650(43.49%) | 4,073(35.67%) | 5,723(37.62%) |
| Type | 4 | 4 | 4 |
| - Choice | 2,222(38.17%) | 8,618(38.74%) | 10,840 (38.62%) |
| - fill-in-the-blank | 1,668(28.65%) | 6,382(28.69%) | 8,050(28.68%) |
| - Yes-no | 18(0.31%) | 88 (0.40%) | 106(0.38%) |
| - Analysis | 1,913(32.86%) | 7,170(32.23%) | 9,083 (32.36%) |
| Level |
| - Level-1 | 12 | 12 | 12 |
| - Level-2 | 319(5.48%) | 1,180(5.30%) | 1,499(5.34%) |
| - Level-3 | 439(7.54%) | 1,648(7.41%) | 20,87(7.44%) |
| - Level-3 | 444(7.63%) | 1,680(7.55%) | 2,124(7.57%) |
| - Level-4 | 574(9.86%) | 2,210(9.93%) | 2,784(9.92%) |
| - Level-5 | 534(9.17%) | 1,939(8.72%) | 2,473(8.81%) |
| - Level-6 | 463(7.95%) | 1,783(8.01%) | 2,246(8.00%) |
| - Level-7 | 458(7.87%) | 1,751(7.87%) | 2,209(7.87%) |
| - Level-8 | 361(6.20%) | 1,372(6.17%) | 1,733(6.17%) |
| - Level-9 | 493(8.47%) | 1,900(8.54%) | 2,393(8.53%) |
| - Level-10 | 587(10.08%) | 2,284(10.27%) | 2,871(10.23%) |
| - Level-11 | 646(11.10%) | 2,512(11.29%) | 3,158(11.25%) |
| - Level-12 | 503(8.64%) | 1,989(8.94%) | 2,492(8.88%) |
| Subjects |
| - Analytic Geometry | 13 | 13 | 13 |
| - Metric Geometry | 707(12.15%) | 2,756(12.39%) | 3,463(12.34%) |
| - Solid Geometry | 738(12.68%) | 2,876(12.93%) | 3,614(12.88%) |
| - Arithmetic | 546(9.38%) | 2,092(9.40%) | 2,638(9.40%) |
| - Arithmetic | 1,999(34.34%) | 7,855(35.31%) | 9,854(35.11%) |
| - Algebra | 676(11.61%) | 2,640(11.87%) | 3,316(11.81%) |
| - Counting | 407(6.99%) | 1,546(6.95%) | 1,953(6.96%) |
| - Transformation Geometry | 85(1.46%) | 274(1.23%) | 359(1.28%) |
| - Graph Theory | 26(0.45%) | 44(0.20%) | 70(0.25%) |
| - Combinatorial Geometry | 140(2.41%) | 495(2.22%) | 635(2.26%) |
| - Combinatorics | 217(3.73%) | 747(3.36%) | 964(3.43%) |
| - Logic | 127(2.18%) | 416(1.87%) | 551(1.96%) |
| - Descriptive Geometry | 135(2.32%) | 465(2.09%) | 603(2.15%) |
| - Statistics | 18(0.31%) | 42(0.19%) | 60(0.21%) |

the power of LMMs while ignoring how to improve their performance. Fourth, our datasets are diverse, with rich subjects and problem types across 12 grades, which can more deeply distinguish models' performance in different mathematical contexts. CMM-Math provides 11 knowledge points and multiple problem types, including choice, yes-no, fill-in-the-blank, and analysis. In addition,



the CMM-Math problems are derived from real math tests in primary, middle, and high school, covering a wider range of grades than the GSM8K, which only includes primary school knowledge. CMM-Math can better test the problem-solving ability of the model at different stages. Finally, our dataset has detailed analysis and rich question stem content, which can enhance the mathematical reasoning ability of the model.

# 4 Our Proposed Method

In this paper, we propose a math-specific LMM (Math-LMM) as a strong baseline for multimodal math reasoning, as illustrated in Figure 3. To tackle the problems with multiple figures, we introduce a mixed instruction with the interleaved text and image inputs. Inspired by LLaVa [23], Math-LMM primarily comprises a Vision Encoder for encoding image information, an Adapter for modality alignment, and a Large Language Model (LLM) for mathematical reasoning. Moreover, to capture the abilities of math reasoning, we train our model using three stages: 1) the foundation pre-training stage aligns general visual information with LLMs via text-image pairs; 2) the foundation fine-tuning stage learns general multimodal abilities based on foundation instructions; and 3) the mathematical fine-tuning stage uses instruction learning based on math instructions to learn multimodal mathematical reasoning.

We translate the input sample as a mix instruction to train Math-LMM. The template instruction is "This is text. [IMAGE1]. This is text. ... This is text. [IMAGE2], [IMAGE3] ..., "where [IMAGE] is the image embedding after alignment. First, we input the images into the vision encoder (e.g., ViT [9], DFN-5B-H-14+ [10]) to obtain the image representation with a fixed dimension. The vision encoder is pre-trained on large-scale visual or multimodal datasets, which can embed the image effectively. Then, we obtain the image embedding [IMAGE] by aligning the image representation with LLM using an adapter. Common designs for the adapter include Cross-Attention [14], Q-Former [21], and MLP. We chose a simple but equally effective two-layer MLP with GELU functions for our Adapter. Finally, we input the mixed restructure with interleaved image-text inputs to LLMs (e.g., Qwen2-7B-Instruct [3]).

In the first foundational pre-training phase, we pre-train the adapter to align the image input with the LLM using large-scale general multimodal datasets with image descriptions. In particular, we only update the parameters of the adapter and fix the parameters of the LLM and encoder. Here, we select several datasets for adapter pre-training, including LLaVA-Pretrain and LLaVA-CC3M-Pretrain-595K [23], and Mantis-Instruct [19].

In the foundational fine-tuning phase, we focus on learning task processing capability using instruction tuning. We train the parameters of both the Adapter and the LLM modules via large-scale foundation instructions. We primarily use datasets involving general domain problems, such as ShareGPT-40$^{2}$, MMDU [25], lllavan-zh-300k [23], and CogVLM-SFT-311K [23, 42].

In the third mathematical fine-tuning phase, we fine-tune the proposed Math-LMM for improved mathematical capabilities by adjusting both the Adapter and LLM modules. We train our model on mathematics-related datasets, including our proposed CMM-Math,

GSM8K [6], competition Maths [18], blossom-math-v4$^{3}$, Vietnamese-395k-meta-math-MetaMathQA-gg-translated, Vietnamese-meta-math-MetaMathQA-40K-gg-translated, and Vietnamese-microsoft-orca-math-word-problems-200k-gg-translated $^{4}$.

# 5 Experiments

# 5.1 Experimental Setups

Selected LMMs. We evaluate a series of LLMs on CMM-Math, including the current state-of-the-art open-source and closed-source models. Particularly, we select InternLM-XComposer2.5-VL (InternLM-VL) [39], Qwen2-VL-Instruct [34] and CogVLM2-Ilama3-Chinesechat (CogVLM2) [35] for open-source models, and for closed-source models, we employ Qwen-VL [3], Gemini [31] and GPT-4o [28].

Datasets and Evaluation Metrics. First, we evaluate the performance of typical LMMs on CMM-Math. Then, we conduct experiments to verify the effectiveness of MATH-LMM over MATHVISTA [26] and MATH-V [33] datasets. In this paper, we employ the Accuracy and GPT-4o scores to measure the performance of our model and baselines. Particularly, we use accuracy for choice and yes-no problems, and use the GPT-4o score for fill-in-the-blank, and analysis problems. For the GPT-4o score, we use GPT-4o to calculate the scores of generated answers by giving the problems, solutions, answers, and generated responses. Specially, the prompt we designed is shown in Figure 3.

Implementation Details. We employ a lightweight DFN5B-H-14+ [10] as the vision encoder. This model is trained on a large amount of high-quality paired image-text data using Contrastive Language Image Pre-training (CLIP) and demonstrates superior performance at a comparable scale of parameters. The image encoding module contains only 0.6 billion parameters, which enables our 7B model to perform inference deployment on a single 4090 GPU. In addition, we select an open-source, high-performance Qwen2 [3] as our large language model module.

# 5.2 Evaluating SOTA LMMs on CMM-Math

We evaluate the performance of several SOTA LMMs over CMM-Math in terms of accuracy (Table 4 and Table 5) and GPT-4o score (Table 6 and Table 7). We also report the performance of various subjects and levels to analyze the LMM's abilities of multimodal mathematical reasoning. We give the analysis in two parts: attention to CMM-Math and attention to SOTA LMMs.

Attention to CMM-Math. We analyze CMM-Math from five perspectives: challenges of CMM-Math, comparisons across different subjects and levels, disparity between accuracy and GPT-46 score, and zero-shot versus few-shot scenarios.

Challenges of CMM-Math. From the last row of Table 4 and Table 5, we can observe that the average results across all models are only 35.66. In some subjects, the average results are even below 30, such as combinatorial, descriptive, solid geometry, and graph theory. Meanwhile, GPT-4o (3-Shot) achieves the best result with a score of 65.98 among all models. However, GPT-4o (3-Shot) still performs poorly on difficult levels, like Levels 9 and 10, and faces challenges in certain subjects, such as combinatorial, descriptive, and solid geometry. This indicates that achieving good results on



<div style="display: block; width: 100%"><img src="https://storage.simpletex.cn/view/m1a11ffe34e400dd12eb858140a8619ef" style="width: 26%; max-width: 26%" /></div> Stage 1: Foundational Pre-training Interleaved text and image inputs

<div style="display: block; width: 100%"><img src="https://storage.simpletex.cn/view/m0afc6c8b4bf1752d99bd64771df98929" style="width: 26%; max-width: 26%" /></div> Stage 3: Mathematical Fine-tuning Interleaved text and image inputs

<div style="display: block; width: 100%"><img src="https://storage.simpletex.cn/view/m0cdb9e87e2d05c823e4441165238c1cd" style="width: 26%; max-width: 26%" /></div> Stage 2: Foundational Fine-tuning Interleaved text and image inputs Figure 3: The diagram of our Math-LMM framework.

Table 4: Comparison of model performances in accuracy across different levels. The levels from 1 to 12 correspond to grade from primary to high school. The first and second highest accuracy of open-source LMMs are marked in red and blue.

| Models | Overall | LV1 | LV2 | LV3 | LV4 | LV5 | LV6 | LV7 | LV8 | LV9 | LV10 | LV11 | LV12 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Open-source LMMs |
| CogVLM2 | 25.85 | 38.00 | 36.36 | 21.15 | 29.38 | 20.39 | 24.32 | 27.32 | 29.33 | 24.90 | 23.02 | 25.37 | 22.73 |
| InternLM-VL | 19.82 | 18.00 | 15.91 | 20.19 | 12.99 | 6.58 | 28.83 | 23.90 | 26.00 | 26.97 | 13.06 | 22.69 | 20.63 |
| Qwen2-VL-Instruct | 43.04 | 54.00 | 57.95 | 49.04 | 49.72 | 33.55 | 48.65 | 47.80 | 46.00 | 41.08 | 37.46 | 38.81 | 38.46 |
| LLaVA-v1.5 | 18.08 | 40.00 | 27.27 | 27.88 | 21.47 | 17.76 | 25.23 | 15.12 | 18.67 | 18.67 | 15.81 | 12.84 | 9.09 |
| LLaVA-v1.6-mistral | 16.83 | 33.00 | 19.32 | 25.00 | 18.64 | 16.45 | 13.51 | 16.59 | 14.67 | 10.37 | 15.12 | 18.51 | 14.34 |
| CogVLM2 (3-Shot) | 31.21 | 37.00 | 34.09 | 40.38 | 29.94 | 28.95 | 35.14 | 34.63 | 32.67 | 28.22 | 28.52 | 32.84 | 25.52 |
| InternLM-VL (3-Shot) | 25.09 | 22.00 | 32.95 | 27.88 | 16.95 | 11.84 | 27.93 | 25.37 | 26.67 | 24.90 | 24.05 | 26.87 | 31.82 |
| Qwen2-VL-Instruct (3-Shot) | 46.29 | 38.00 | 62.50 | 53.85 | 55.93 | 54.61 | 60.36 | 47.80 | 46.00 | 44.81 | 40.89 | 36.42 | 43.01 |
| LLaVA-v1.5 (3-Shot) | 19.69 | 37.00 | 28.41 | 37.50 | 24.86 | 24.34 | 30.63 | 11.22 | 16.67 | 9.54 | 19.93 | 13.13 | 18.18 |
| LLaVA-v1.6-mistral (3-Shot) | 21.88 | 17.00 | 35.23 | 31.73 | 32.20 | 26.97 | 30.63 | 20.00 | 17.33 | 7.47 | 16.84 | 24.18 | 21.68 |
| Closed-source LMMs |
| Qwen-VL-Max | 32.10 | 32.00 | 44.32 | 37.50 | 35.59 | 32.24 | 35.14 | 32.20 | 28.67 | 32.37 | 30.58 | 31.94 | 26.22 |
| Math-LMM (Ours 72B) | 48.57 | 47.00 | 62.50 | 53.85 | 59.32 | 48.03 | 58.56 | 51.71 | 43.33 | 38.59 | 46.05 | 44.78 | 48.60 |
| Closed-source LMMs |
| Qwen-VL-Max | 49.91 | 70.00 | 62.50 | 56.73 | 54.80 | 46.71 | 67.57 | 46.83 | 43.33 | 41.08 | 45.70 | 48.96 | 46.85 |
| Gemini | 41.88 | 65.00 | 65.91 | 58.65 | 51.41 | 46.05 | 56.76 | 39.02 | 39.33 | 34.85 | 35.40 | 35.52 | 29.72 |
| GPT-4o | 29.02 | 46.00 | 43.18 | 38.46 | 33.90 | 32.89 | 32.43 | 27.32 | 24.67 | 28.63 | 19.59 | 27.76 | 23.78 |
| Qwen-VL-Max (3-Shot) | 64.91 | 60.00 | 76.14 | 72.12 | 69.49 | 57.24 | 71.17 | 64.39 | 58.67 | 52.70 | 66.67 | 68.06 | 67.83 |
| Gemini (3-Shot) | 41.65 | 69.00 | 64.77 | 52.88 | 41.24 | 46.05 | 55.86 | 38.54 | 41.33 | 39.83 | 33.33 | 33.73 | 34.97 |
| GPT-4o (3-Shot) | 65.98 | 80.00 | 84.09 | 75.00 | 81.92 | 69.74 | 72.07 | 68.78 | 61.33 | 56.85 | 52.23 | 66.57 | 59.44 |
| Mean accuracy of LMMs | 35.66 | 44.61 | 47.41 | 43.32 | 39.99 | 34.47 | 43.04 | 35.47 | 34.15 | 31.21 | 31.35 | 33.83 | 32.38 |

CMM-Math is challenging for most current LMMs, and even the best LMMs struggle to perform exceptionally well on CMM-Math.

is 35.66, with LMMs achieving an accuracy exceeding 40 in arithmetic and statistics subjects. In contrast, in geometry, including analytical, combinatorial, descriptive, metric, and transformation geometry, the accuracy of LMMs is below 35.66, with the worst performance at 23.17 for descriptive geometry.

Comparisons Across Different Levels. Most LMMs perform well on primary school-level problems, but their performance declines at the high school level. As indicated in the last row of Table 4 and Table 6, the mean accuracy of LMMs shows an overall downward trend. Specifically, for instance, when employing three-shot prompting with GPT-4o, the model achieves an accuracy of 84.08 on level 2 but only 52.23 on level 10. This phenomenon can also be more intuitively observed in Figure 1, where for most models, the shaded area representing lower grade levels in the upper semicircle is significantly larger than the area representing higher grade levels in the lower semicircle.

Comparisons Across Different Subjects. Most LMMs excel in arithmetic and statistics but show limited proficiency in geometry. We can observe that the mean accuracy of all LMMs across all subjects

Disparity Between Accuracy and GPT-4o Score. When comparing the performance of LMMs in both accuracy and GPT-4o score, we observe that closed-source models maintain consistent performance while open-source models show inconsistencies. Specifically, GPT-4o consistently ranks highest, while Gemini ranks lowest. CogVLM2 has higher accuracy than InternLM-VL but is lower on the GPT-4o score. This discrepancy may arise from differences in the training data distribution, where the datasets might focus more on choice and yes-no questions while lacking materials for problem-solving and analytical tasks. Moreover, this inconsistency could also result from insufficient training data, leading to models that obtain correct



Table 5: Comparison of model performances in accuracy across various mathematical subjects. Alg: algebra, AnaG: analytic geometry, Ari: arithmetic, CombG: combinatorial geometry, Comb: combinatorics,Cnt: counting, Desc: descriptive geometry GrphT: graph theory, Log: logic, MetG: metric geometry, SolG: solid geometry, Stat: statistics, TransG: transformation geometry

| Models | Overall | Alg | AnaG | Ari | CombG | Comb | Cnt | Desc | GrphT | Log | MetG | SolG | Stat | TransG |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Open-source LMMs |
| CogVLM2 | 25.85 | 21.94 | 25.22 | 24.76 | 28.85 | 24.68 | 26.54 | 29.79 | 44.44 | 19.05 | 33.79 | 23.36 | 45.45 | 25.58 |
| InternLM-VL | 19.82 | 21.94 | 26.38 | 20.68 | 21.15 | 12.99 | 16.67 | 19.15 | 0.00 | 9.52 | 20.48 | 12.15 | 27.27 | 13.95 |
| Qwen2-VL-Instruct | 43.04 | 36.45 | 42.03 | 50.65 | 36.54 | 40.26 | 45.68 | 27.66 | 44.44 | 39.68 | 43.34 | 37.85 | 45.45 | 37.21 |
| LLaVA-v1.5 | 18.08 | 15.16 | 13.91 | 21.82 | 15.38 | 18.18 | 12.96 | 21.28 | 22.22 | 12.70 | 19.45 | 19.16 | 36.36 | 25.58 |
| LLaVA-v1.6-mistral | 16.83 | 17.10 | 16.52 | 22.31 | 7.69 | 11.69 | 10.49 | 8.51 | 0.00 | 19.05 | 13.99 | 15.42 | 27.27 | 16.28 |
| CogVLM2 (3-Shot) | 31.21 | 30.97 | 28.12 | 32.57 | 32.69 | 24.68 | 30.25 | 29.79 | 22.22 | 25.40 | 36.18 | 30.84 | 45.45 | 27.91 |
| InternLM-VL (3-Shot) | 25.09 | 29.03 | 30.14 | 24.76 | 15.38 | 27.27 | 25.93 | 12.77 | 0.00 | 26.98 | 24.57 | 17.76 | 9.09 | 25.58 |
| Qwen2-VL-Instruct (3-Shot) | 46.29 | 37.42 | 40.58 | 53.42 | 46.15 | 40.26 | 56.17 | 36.17 | 33.33 | 46.03 | 49.15 | 40.19 | 54.55 | 51.16 |
| LLaVA-v1.5 (3-Shot) | 19.69 | 19.03 | 14.20 | 28.66 | 3.85 | 23.38 | 21.60 | 14.89 | 11.11 | 15.87 | 14.68 | 16.36 | 45.45 | 2.33 |
| LLaVA-v1.6-mistral (3-Shot) | 21.88 | 22.26 | 17.97 | 32.25 | 5.77 | 20.78 | 22.22 | 4.26 | 11.11 | 28.57 | 15.70 | 13.55 | 27.27 | 16.28 |
| Math-LMM (Ours 7B) | 32.10 | 26.13 | 29.86 | 36.64 | 28.85 | 32.47 | 35.19 | 27.66 | 33.33 | 30.16 | 35.15 | 28.04 | 36.36 | 25.58 |
| Math-LMM (Ours 72B) | 48.57 | 48.06 | 44.35 | 60.59 | 32.69 | 50.65 | 53.70 | 17.02 | 22.22 | 57.14 | 44.03 | 35.98 | 63.64 | 27.91 |
| Closed-source LMMs |
| Qwen-VL-Max | 49.91 | 49.68 | 48.12 | 60.59 | 44.23 | 50.65 | 54.94 | 21.28 | 11.11 | 50.79 | 42.66 | 36.45 | 63.64 | 51.16 |
| Gemini | 41.88 | 36.77 | 37.97 | 55.37 | 26.92 | 37.66 | 48.15 | 31.91 | 33.33 | 26.98 | 37.54 | 32.71 | 54.55 | 25.58 |
| GPT-4o | 29.02 | 26.13 | 28.41 | 35.67 | 26.92 | 20.78 | 32.10 | 25.53 | 33.33 | 28.57 | 24.57 | 21.96 | 18.18 | 37.21 |
| Qwen-VL-Max (3-Shot) | 64.91 | 70.00 | 63.19 | 74.43 | 50.00 | 66.23 | 69.75 | 21.28 | 44.44 | 73.02 | 54.61 | 57.01 | 63.64 | 53.49 |
| Gemini (3-Shot) | 41.65 | 38.71 | 35.07 | 54.07 | 19.23 | 31.17 | 51.85 | 27.66 | 44.44 | 44.44 | 36.18 | 30.84 | 54.55 | 44.19 |
| GPT-4o (3-Shot) | 65.98 | 62.90 | 59.71 | 82.57 | 46.15 | 66.23 | 72.84 | 40.43 | 77.78 | 68.25 | 59.04 | 47.66 | 81.82 | 55.81 |
| Mean accuracy of LMMs | 35.66 | 33.87 | 33.43 | 42.88 | 27.14 | 33.33 | 38.17 | 23.17 | 27.16 | 34.57 | 33.62 | 28.74 | 44.44 | 31.27 |

Table 6: Comparison of model performances in GPT-4o score across different levels. The levels from 1 to 12 correspond to primary to high school grades. The maximum score is 10.

| Models | Overall | LV1 | LV2 | LV3 | LV4 | LV5 | LV6 | LV7 | LV8 | LV9 | LV10 | LV11 | LV12 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Open-source LMMs |
| CogVLM2 | 2.82 | 2.96 | 3.66 | 3.52 | 2.99 | 2.29 | 2.90 | 2.46 | 3.05 | 2.37 | 2.43 | 2.45 | 2.43 |
| InternLM-VL | 4.48 | 4.05 | 5.54 | 5.27 | 4.90 | 4.20 | 5.12 | 4.00 | 4.03 | 2.60 | 4.13 | 4.41 | 4.35 |
| Qwen2-VL-Instruct | 5.26 | 4.23 | 5.54 | 6.07 | 5.40 | 5.18 | 6.05 | 5.51 | 5.53 | 4.21 | 4.99 | 4.94 | 4.64 |
| LLAva-v1.5 | 2.56 | 2.51 | 2.80 | 2.96 | 2.76 | 2.50 | 2.37 | 2.66 | 2.66 | 2.37 | 2.43 | 2.27 | 2.34 |
| LLAva-v1.6-mistral | 2.81 | 2.55 | 2.88 | 2.94 | 2.57 | 2.43 | 2.42 | 2.91 | 3.36 | 3.85 | 3.04 | 2.68 | 2.59 |
| CogVLM2 (3-Shot) | 2.72 | 2.73 | 3.53 | 3.18 | 2.78 | 2.30 | 2.66 | 2.35 | 2.97 | 2.31 | 2.46 | 2.48 | 2.74 |
| InternLM-VL (3-Shot) | 4.35 | 3.95 | 5.46 | 5.06 | 4.62 | 3.77 | 4.78 | 3.96 | 4.05 | 3.08 | 4.11 | 4.31 | 4.36 |
| Qwen2-VL-Instruct (3-Shot) | 4.09 | 3.94 | 4.99 | 4.94 | 4.28 | 3.82 | 4.73 | 3.75 | 4.06 | 3.28 | 3.61 | 3.49 | 3.47 |
| LLAva-v1.5 (3-Shot) | 3.34 | 2.75 | 2.75 | 3.10 | 2.70 | 3.14 | 2.49 | 3.77 | 4.89 | 5.79 | 3.75 | 2.88 | 3.42 |
| LLAVA-v1.6-mistral (3-Shot) | 3.78 | 3.27 | 3.28 | 3.50 | 3.30 | 3.86 | 2.62 | 3.78 | 5.67 | 6.23 | 4.31 | 3.05 | 3.73 |
| Math-LMM (Ours 7B) | 2.46 | 2.27 | 3.17 | 2.95 | 2.97 | 2.40 | 1.83 | 2.16 | 2.67 | 2.16 | 2.13 | 2.26 | 2.11 |
| Math-LMM (Ours 72B) | 4.04 | 3.61 | 4.66 | 4.52 | 3.71 | 3.97 | 4.49 | 3.81 | 3.84 | 3.64 | 4.00 | 3.93 | 3.86 |
| Closed-source LMMs |
| Qwen-VL-Max | 6.50 | 5.91 | 7.30 | 7.54 | 7.11 | 6.61 | 7.02 | 6.1 | 5.91 | 4.73 | 6.01 | 6.18 | 6.17 |
| Gemini | 6.02 | 6.30 | 6.85 | 6.83 | 6.46 | 5.75 | 6.40 | 5.67 | 6.46 | 5.01 | 5.42 | 4.96 | 5.62 |
| GPT-4o | 7.94 | 7.44 | 8.70 | 8.76 | 8.34 | 8.04 | 8.30 | 7.83 | 7.65 | 6.44 | 7.67 | 7.48 | 7.74 |
| Qwen-VL-Max (3-Shot) | 6.21 | 5.66 | 6.70 | 6.43 | 6.18 | 6.12 | 6.91 | 6.00 | 5.72 | 5.50 | 5.67 | 6.57 | 6.51 |
| Gemini (3-Shot) | 5.89 | 5.83 | 6.54 | 6.47 | 6.06 | 5.44 | 6.26 | 5.51 | 6.59 | 5.36 | 5.77 | 5.21 | 5.44 |
| GPT-4o (3-Shot) | 7.85 | 7.27 | 8.53 | 8.63 | 8.45 | 8.09 | 8.36 | 7.87 | 7.65 | 6.06 | 7.48 | 7.22 | 7.46 |
| Mean accuracy of LMMs | 4.62 | 4.29 | 5.16 | 5.15 | 4.75 | 4.44 | 4.76 | 4.45 | 4.82 | 4.17 | 4.41 | 4.26 | 4.39 |

answers but struggle to provide high-quality analytical processes. This highlights that our CMM-Math, unlike other math test sets that offer only choice questions, provides a more comprehensive evaluation of models' analytical and problem-solving abilities.

Zero-shot versus 3-shot Scenarios. All few-shot models perform better than zero-shot prompting in terms of accuracy. This indicates that few-shot prompting helps models obtain correct answers. Conversely, regarding the GPT-40 score, most models perform better



Table 7: Comparison of model performances in GPT-4o score across various mathematical subjects.

| Models | Overall | Alg | AnaG | Ari | CombG | Comb | Cnt | Desc | GrphT | Log | MetG | SolG | Stat | TransG |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Open-source LMMs |
| CogVLM2 | 2.82 | 2.60 | 2.44 | 3.21 | 2.81 | 2.44 | 2.29 | 2.05 | 2.41 | 2.89 | 2.91 | 2.41 | 2.71 | 3.36 |
| InternLM-VL | 4.48 | 4.51 | 4.02 | 5.24 | 2.69 | 4.28 | 4.08 | 2.11 | 3.82 | 4.75 | 4.16 | 3.78 | 5.14 | 3.07 |
| Qwen2-VL-Instruct | 5.26 | 5.73 | 4.77 | 6.07 | 3.81 | 4.30 | 4.87 | 3.69 | 2.94 | 4.92 | 4.71 | 4.38 | 7.43 | 4.00 |
| LLaVA-1.5 | 2.56 | 2.46 | 2.38 | 2.72 | 2.45 | 2.30 | 2.56 | 2.51 | 2.35 | 2.31 | 2.37 | 2.63 | 3.43 | 2.90 |
| LLaVA-v1.6-mistral | 2.81 | 2.47 | 3.35 | 2.68 | 2.73 | 2.60 | 3.09 | 3.57 | 3.71 | 2.52 | 2.93 | 2.61 | 3.86 | 3.74 |
| CogVLM2 (3-Shot) | 2.72 | 2.53 | 2.62 | 2.94 | 2.42 | 2.59 | 2.65 | 1.90 | 2.12 | 2.84 | 2.68 | 2.51 | 2.57 | 3.14 |
| InternLM-VL (3-Shot) | 4.35 | 4.58 | 4.14 | 5.08 | 2.91 | 4.25 | 3.73 | 2.06 | 3.06 | 4.44 | 3.91 | 3.65 | 4.71 | 2.93 |
| Qwen2-VL-Instruct (3-Shot) | 4.09 | 3.83 | 3.67 | 4.91 | 3.61 | 3.34 | 3.60 | 3.26 | 2.82 | 3.53 | 3.75 | 3.23 | 4.54 | 2.95 |
| LLaVA-v1.5 (3-Shot) | 3.34 | 2.91 | 3.92 | 2.74 | 5.36 | 2.76 | 3.23 | 5.27 | 3.82 | 2.95 | 4.04 | 3.86 | 3.43 | 4.90 |
| LLaVA-v1.6-mistral (3-Shot) | 3.78 | 3.27 | 4.07 | 2.94 | 5.90 | 3.08 | 3.51 | 6.24 | 4.82 | 3.27 | 5.05 | 5.02 | 2.43 | 4.83 |
| Closed-source LMMs |
| Qwen-VL-Max | 2.46 | 2.19 | 2.23 | 2.76 | 2.40 | 1.90 | 1.84 | 2.41 | 2.06 | 2.62 | 2.40 | 2.53 | 1.43 | 2.43 |
| Gemini | 6.02 | 5.65 | 5.29 | 6.72 | 5.72 | 5.15 | 5.32 | 4.65 | 3.82 | 6.16 | 6.12 | 5.86 | 6.29 | 5.07 |
| GPT-4o | 7.94 | 8.15 | 7.28 | 8.65 | 6.23 | 7.89 | 7.70 | 6.22 | 7.41 | 7.56 | 7.65 | 7.20 | 6.00 | 5.05 |
| Qwen-VL-Max (3-Shot) | 6.21 | 6.52 | 6.14 | 6.73 | 4.74 | 5.44 | 5.45 | 5.74 | 5.59 | 6.06 | 5.96 | 5.81 | 8.00 | 7.14 |
| Gemini (3-Shot) | 5.89 | 5.72 | 5.41 | 6.45 | 5.62 | 5.49 | 5.36 | 5.34 | 6.18 | 5.33 | 5.78 | 5.41 | 6.14 | 5.02 |
| GPT-4o (3-Shot) | 7.85 | 7.99 | 7.07 | 8.61 | 6.12 | 7.74 | 7.51 | 6.31 | 8.24 | 7.52 | 7.46 | 7.22 | 8.57 | 6.90 |
| Mean accuracy of LMMs | 4.62 | 4.56 | 4.36 | 5.02 | 4.03 | 4.18 | 4.23 | 3.99 | 4.07 | 4.41 | 4.54 | 4.29 | 4.97 | 4.19 |

Table 8: Accuracy scores on the testmini subset of MathVista. FQA: figure question answering, GPS: geometry problem solving, MWP: math word problem, TQA: textbook question answering, VQA: visual question answering. Mathematical reasoning types: ALG: algebraic reasoning, ARI: arithmetic reasoning, GEO: geometry reasoning, LOG: logical reasoning, NUM: numeric commonsense, SCI: scientific reasoning, STA: statistical reasoning.

| Model | Overall | FQA | GPS | MWP | TQA | VQA | ALG | ARI | GEO | LOG | NUM | SCI | STA |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Open-source LMMs |
| IDEFICS-9B-Instruct | 19.8 | 21.6 | 21.1 | 6.5 | 25.9 | 24.0 | 22.1 | 15.0 | 19.8 | 18.9 | 9.9 | 24.6 | 18.1 |
| mPLUG-OwI-LLAMA-7B | 22.2 | 22.7 | 23.6 | 10.2 | 27.2 | 27.9 | 23.6 | 19.2 | 23.9 | 13.5 | 12.7 | 26.3 | 21.4 |
| miniGP4-LLAMA-2-7B | 23.1 | 18.6 | 26.0 | 13.4 | 30.4 | 30.2 | 28.1 | 21.0 | 24.7 | 16.2 | 16.7 | 25.4 | 17.9 |
| LLaMA-Adapter-V2-7B | 23.9 | 21.2 | 25.5 | 11.3 | 32.3 | 31.8 | 26.3 | 20.4 | 24.3 | 24.3 | 13.9 | 29.5 | 18.3 |
| LLaVAR | 25.2 | 21.9 | 25.0 | 16.7 | 34.8 | 30.7 | 24.2 | 22.1 | 23.0 | 13.5 | 15.3 | 42.6 | 21.9 |
| InstructBLIP-Vicuna-7B | 25.3 | 23.1 | 20.7 | 18.3 | 32.3 | 35.2 | 21.8 | 27.1 | 20.7 | 18.9 | 20.4 | 33.0 | 23.1 |
| LLaVA-LLAMA-2-13B | 26.1 | 26.8 | 29.3 | 16.1 | 32.3 | 26.3 | 27.3 | 20.1 | 28.8 | 24.3 | 18.3 | 37.3 | 25.1 |
| Math-LMM (Ours 7B) | 34.9 | 25.3 | 46.6 | 46.2 | 34.2 | 24.6 | 43.1 | 30.3 | 45.6 | 16.2 | 27.1 | 28.6 | 25.9 |
| Math-LMM (Ours 72B) | 36.3 | 36.4 | 33.7 | 46.2 | 36.1 | 29.1 | 29.9 | 34.6 | 33.5 | 24.3 | 28.5 | 41.8 | 40.2 |
| Closed-source LMMs |
| Multimodal Bard | 34.8 | 26.0 | 47.1 | 29.6 | 48.7 | 26.8 | 46.5 | 28.6 | 47.8 | 13.5 | 14.9 | 47.5 | 33.0 |
| GPT-4V (Playground) | 49.9 | 43.1 | 50.5 | 57.5 | 65.2 | 38.0 | 53.0 | 49.0 | 51.0 | 21.6 | 20.1 | 63.1 | 55.8 |
| Human Performance |
| Human performance | 60.3 | 59.7 | 48.4 | 73.0 | 63.2 | 55.9 | 50.9 | 59.2 | 51.4 | 40.7 | 53.8 | 64.9 | 63.9 |

with zero-shot prompting than with few-shot prompting, except for the LLaVA-v1.5 and LLaVA-v1.6-mistral models. This suggests that few-shot prompting does not necessarily lead to higher quality outputs and analyses. Our view is that the content of few-shot prompts may influence how models conduct their own analysis and reasoning, potentially leading to poorer performance.

Attention to SOTA LMMs. We separately provide an analysis of the performance of closed-source and open-source LMMs.

Closed-source LMMs. We observe that all closed-source models significantly outperform open-source models. Both in terms of accuracy and GPT-4o score, GPT-4o and Qwen-VL demonstrate the best performance on the CMM-Math in most cases. However, we note that GPT-4o performs optimally on simple and moderately difficult levels, while Qwen-VL excels on the most challenging levels, including levels 10, 11, and 12. This suggests that Qwen-VL may have a stronger advantage in handling more complex problems.



Table 9: Comparison of model performances on MATH-V across various mathematical subjects. Alg: algebra, AnaG: analytic geometry, Ari: arithmetic, CombG: combinatorial geometry, Comb: combinatorics, Cnt: counting, DescG: descriptive geometry, GrphT: graph theory, Log: logic, Angle: metric geometry - angle, Area: metric geometry - area, Len: metric geometry-length, SolG: solid geometry, Stat: statistics, Topo: topology, TransG: transformation geometry.

| Model | Overall | Alg | AnaG | Ari | CombG | Comb | Cnt | DescG | GrphT | Log | Angle | Area | Len | SolG | Stat | Topo | TransG |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Open-source LMMs |
| LLaVA-v1.5-7B | 8.52 | 7.00 | 7.10 | 10.70 | 7.10 | 4.80 | 10.50 | 7.70 | 10.00 | 9.20 | 15.60 | 10.20 | 9.80 | 5.30 | 8.60 | 4.40 | 4.80 |
| SPHINX (V2) | 9.70 | 6.70 | 7.10 | 12.90 | 7.50 | 7.70 | 6.00 | 9.60 | 16.70 | 10.10 | 11.80 | 11.80 | 12.50 | 8.20 | 8.60 | 8.70 | 6.00 |
| ShareGPT4V-7B | 10.53 | 5.50 | 3.60 | 12.90 | 10.10 | 4.80 | 7.50 | 11.50 | 14.40 | 10.90 | 16.20 | 11.80 | 12.30 | 9.80 | 15.50 | 17.40 | 11.30 |
| LLaVA-v1.5-13B | 11.12 | 7.00 | 14.30 | 14.30 | 9.10 | 6.60 | 6.00 | 13.50 | 5.60 | 13.50 | 10.40 | 12.60 | 14.70 | 11.50 | 13.80 | 13.00 | 10.70 |
| ShareGPT4V-13B | 11.88 | 7.50 | 15.50 | 16.40 | 10.70 | 8.90 | 9.00 | 11.50 | 8.90 | 7.60 | 11.60 | 13.00 | 17.40 | 10.30 | 8.60 | 8.70 | 12.50 |
| SPHINX-MoE | 14.18 | 7.80 | 17.90 | 14.30 | 15.60 | 9.50 | 11.90 | 12.50 | 15.6 | 12.60 | 16.20 | 15.60 | 17.80 | 13.50 | 12.10 | 8.70 | 16.10 |
| InternLM-VL | 14.54 | 9.30 | 15.50 | 12.10 | 15.30 | 11.30 | 10.50 | 14.40 | 22.20 | 19.30 | 19.70 | 15.6 | 15.00 | 11.90 | 15.50 | 26.10 | 15.50 |
| Math-LMM (Ours 7B) | 11.58 | 7.30 | 8.30 | 10.70 | 14.00 | 7.10 | 7.40 | 16.40 | 12.20 | 9.20 | 14.50 | 10.60 | 14.90 | 9.00 | 8.60 | 26.10 | 16.70 |
| Math-LMM (Ours 72B) | 17.53 | 10.70 | 28.60 | 15.00 | 20.10 | 11.30 | 11.90 | 15.40 | 16.70 | 21.00 | 22.50 | 18.40 | 20.00 | 15.60 | 20.70 | 8.70 | 19.60 |
| Closed-source LMMs |
| Qwen-VL-Plus | 10.72 | 11.30 | 17.90 | 14.30 | 12.70 | 4.80 | 10.50 | 15.40 | 8.90 | 14.30 | 11.60 | 6.40 | 10.00 | 14.30 | 6.90 | 8.70 | 11.31 |
| Qwen-VL-Max | 15.59 | 10.70 | 19.10 | 20.00 | 16.90 | 12.50 | 17.90 | 16.40 | 12.20 | 21.00 | 13.30 | 14.20 | 19.80 | 11.50 | 20.70 | 13.00 | 17.30 |
| Gemini Pro | 17.66 | 15.10 | 10.70 | 20.70 | 20.10 | 11.90 | 7.50 | 20.20 | 21.10 | 16.80 | 19.10 | 19.00 | 20.00 | 14.30 | 13.80 | 17.40 | 20.80 |
| GPT-4V | 22.76 | 27.30 | 32.10 | 35.70 | 21.10 | 16.70 | 13.40 | 22.10 | 14.40 | 16.80 | 22.00 | 22.20 | 20.90 | 23.80 | 24.10 | 21.70 | 25.60 |
| Human Performance |
| Human (testmini) | 75.66 | 57.90 | 79.00 | 100.00 | 100.00 | 47.40 | 94.70 | 89.50 | 63.20 | 63.20 | 36.80 | 52.60 | 73.70 | 89.50 | 89.50 | 100.00 | 73.70 |

<div style="display: block; width: 100%"><img src="https://storage.simpletex.cn/view/m7998e0929448dc5efcecb9c3bdea866d" style="width: 36%; max-width: 36%" /></div> Figure 4: The prompt for GPT-4o used for scoring.

Open-source LMMs. In terms of accuracy, our Math-LMM (72B) and Qwen2-VL-Instruct (3-Shot) achieve the best and second-best performances, with scores of 48.57 and 46.29, respectively. On the most challenging levels 10, 11, and 12, Math-LMM (72B) achieves the best results, indicating that Math-LMM has a stronger advantage in handling more complex problems. Furthermore, regarding the GPT-4o score, we notice that Math-LMM achieved only ordinary results, while Qwen2-VL-Instruct obtains the best result of 5.26. This could be because the training data for Math-LMM is still limited, leading to weaker language expression and analytical reasoning capabilities.

# 5.3 Evaluating Math-LMM

To evaluate the effectiveness of our Math-LMM, we conduct experiments on MATHVISTA [26] and MATH-V [33] (Table 8 and Table 9). These two datasets are widely used to evaluate the capability of large multimodal models in solving English mathematical problems.

Main Results over MATHVISTA. We select LMMs used in the MathVista [26] experiments for comparison with Math-LMM, including IDEFICS-9B-Instruct [20], mPLUG-Owl-LLaMA-7B [37], miniGPT4-LLaMA-2-7B [42], LLaMA-Adapter-V2-7B [13], LLaVAR [40], InstructBLIP-Vicuna-7B [7], LLaVA-LLaMA-2-13B [23], Multi-modal Bard [15], and GPT-4V (Playground) [28].

In the results of open-source models shown in Table 8, our Math-LMM achieves the best (36.3) and suboptimal (34.9) results with 72B and 7B versions. Across five problem tasks, Math-LMM (7B) obtains the best performance on two tasks and Math-LMM (72B) achieves the best performance on three tasks and the second-best on one task. Furthermore, our Math-LMM almost achieves the best performance across all types of mathematical reasoning, except for scientific reasoning, where it achieved a suboptimal performance. Additionally, in numeric commonsense problems, both parameter versions of our Math-LMM perform exceptionally well, even surpassing closed-source models such as Multimodal Bard [15] and GPT-4V (Playground). These outcomes suggest that Math-LMM demonstrates commendable capabilities in addressing English multimodal mathematical questions. Detailed comparative analyses of other models can be found in MathVista [26].

Main Results over MATH-V. We also compare our Math-LMM with existing LLMs over MATH-V [33], including Qwen-VL-Plus [4], Qwen-VL-Max [4], Gemini Pro [31], GPT-4V [28], LLaVa-v1.5-7B [23], SPHINX [22], ShareGPT-4V-7B [5], LLaVa-v1.5-13B [23], ShareGPT-4V-13B [5], InternLM-XComposer2-VL [8], and SPHINX-MoE [22].

In Table 9, our Math-LMM (72B) achieves the best performance among in open-source models. Although the Math-LMM (7B) does not achieve the second-best performance, compared to other open-source models of the same parameter scale, such as LLaVa-v1.5-7B [23], SPHINX [22], and ShareGPT-4V-7B [5], Math-LMM (7B) still achieves the best performance. This may be because MATH-V [33] is a more challenging test set than MATHVISTA [26], where model parameter scale has a greater impact on performance. Meanwhile, among open-source models, Math-LMM almost achieves the best performance across all 16 subjects, except for the subjects of arithmetic and graph theory. Notably, compared to closed-source models, Math-LMM also achieves the best performance among all models on the subjects of logic, metric geometry-angle, and topology. These results indicate that Math-LMM also has a certain level of competitiveness on harder English multimodal mathematical problems.

# 6 Conclusion

In this paper, we introduce CMM-Math, a comprehensive Chinese multimodal mathematical dataset designed to evaluate and enhance the performance of LMMs in mathematical reasoning. CMM-Math is distinguished by its scale, diversity, and complexity, comprising over 28,000 high-quality samples that span 12 grade levels and include various problem types. This dataset serves as both a benchmark and a training resource, addressing the gap in non-English, specifically Chinese, multimodal mathematical datasets. Our experiments reveal that existing state-of-the-art LMMs struggle with the challenges posed by the CMM-Math dataset, highlighting the need for further advancements in this field. We also propose a new math-specific LMM, Math-LMM, which is trained through a three-stage process: foundational pre-training, foundational fine-tuning, and mathematical fine-tuning. The results from our evaluations demonstrate that Math-LMM improves performance in multimodal mathematical reasoning by comparing with open-source LMMs.

