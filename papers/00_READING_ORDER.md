# AI Training and Agent Reading Order

This folder is ordered for learning how modern ChatGPT/Claude-like systems are trained, then how AI systems can choose actions as agents rather than follow fixed scripts.

## Core LLM Training Track

01. Attention Is All You Need - Transformer architecture.
02. Improving Language Understanding by Generative Pre-Training - GPT-1, pretrain then fine-tune.
03. BERT - bidirectional pretraining, useful contrast with GPT-style causal models.
04. Language Models are Unsupervised Multitask Learners - GPT-2 and zero-shot behavior.
05. Language Models are Few-Shot Learners - GPT-3 and in-context learning.
06. Scaling Laws for Neural Language Models - why scale, data, and compute matter.
07. Fine-Tuning Language Models from Human Preferences - early RLHF for language.
08. Learning to Summarize from Human Feedback - preference model as reward.
09. Training Compute-Optimal Large Language Models - Chinchilla scaling and data balance.
10. Training Language Models to Follow Instructions with Human Feedback - InstructGPT, closest public recipe behind ChatGPT-style instruction following.
11. Training a Helpful and Harmless Assistant with RLHF - Anthropic assistant alignment.
12. Constitutional AI - Claude-style principle-based feedback and RLAIF.
13. GPT-4 Technical Report - frontier multimodal LLM report.
14. Direct Preference Optimization - simpler preference tuning without full PPO-style RLHF.
15. Llama 2 - open foundation and chat model training details.

## Agent, Tool Use, and Reasoning Track

16. ReAct - interleaving reasoning and actions.
17. Toolformer - learning when and how to use tools.
18. Tree of Thoughts - search over reasoning paths.
19. Reflexion - learning from feedback through verbal memory.
20. Voyager - open-ended embodied LLM agent in Minecraft.
21. Llama 3 Herd of Models - modern open model family with reasoning/tool-use details.
22. OpenAI o1 System Card - large-scale RL for chain-of-thought reasoning.
23. Deliberative Alignment - training models to reason over safety specifications.
24. DeepSeek-R1 - RL-driven reasoning, including R1-Zero.
25. Claude Opus 4 and Sonnet 4 System Card - modern Claude hybrid reasoning and agentic safety context.

## Reinforcement Learning Foundations for "Choosing Actions"

26. Human-Level Control through Deep Reinforcement Learning - DQN learns action policies from pixels and rewards.
27. AlphaGo Zero - self-play RL without human game data.
28. AlphaZero - general self-play RL for chess, shogi, and Go.
29. MuZero - planning with a learned model of dynamics.

Recommended shortcut: read 01, 05, 10, 12, 16, 24, 26, 27 first.
