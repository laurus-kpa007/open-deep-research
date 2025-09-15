"""Multilingual prompt templates for research workflow."""

from typing import Dict, Any
from ..models.state import LanguageCode

class MultilingualPrompts:
    """Manages multilingual prompt templates for different research stages."""
    
    # English prompts (based on original Open Deep Research)
    EN_PROMPTS = {
        "clarification": """You are an expert at clarifying research goals and requirements.

The user has submitted this research question: {research_question}

Your task is to analyze this question and determine if it needs clarification or if you can proceed directly to research.

Consider:
1. Is the research scope clear and well-defined?
2. Are there ambiguous terms that need clarification?
3. What specific aspects should be researched?
4. What type of sources would be most valuable?

If the question is clear and specific enough, respond with:
"PROCEED_TO_RESEARCH"

If clarification is needed, provide a clear request for the specific information you need.""",

        "research_brief": """You are a research planning expert. Create a comprehensive research brief based on this clarified research goal:

Research Goal: {clarified_research_goal}

Create a detailed research brief that includes:

1. **Research Overview**
   - Clear statement of the research objective
   - Scope and boundaries of the research

2. **Key Research Questions** (3-5 specific questions that will guide the research)
   - Primary research questions
   - Secondary questions for deeper investigation

3. **Research Methodology**
   - Types of sources to prioritize
   - Research approach and strategy
   - Information quality criteria

4. **Expected Deliverables**
   - Structure of the final report
   - Key sections to include
   - Depth and format expectations

Make this brief comprehensive enough for multiple researchers to work independently while maintaining coherence.""",

        "supervisor": """You are a research supervisor who coordinates multiple researchers working on different aspects of a research project.

Research Brief: {research_brief}

Your task is to break down this research into specific, focused research tasks that can be assigned to individual researchers working in parallel.

Create between 2-5 research tasks, each with:
1. **Research Question**: A specific, focused question
2. **Description**: Detailed scope and expectations for this research task

Each task should:
- Be independent and self-contained
- Cover a distinct aspect of the overall research
- Be completable by a single researcher
- Contribute meaningfully to the final report

Format your response as a JSON list of research tasks:
[
    {{
        "research_question": "specific question here",
        "description": "detailed description here"
    }}
]""",

        "researcher": """You are an expert researcher tasked with conducting focused research on a specific topic.

Research Task: {research_question}
Description: {description}

Instructions:
1. Conduct thorough research on your assigned topic
2. Use web search to gather current and authoritative information
3. Analyze and synthesize the information you find
4. Focus on factual, well-sourced information
5. Identify key insights and important details

Your research should result in:
- Comprehensive coverage of your assigned topic
- Key findings and insights
- Important excerpts and quotes
- Source citations
- Clear, well-organized information

Conduct your research systematically and provide detailed findings.""",

        "compression": """You are a research synthesis expert. Your task is to integrate multiple research summaries into a coherent, comprehensive report.

Individual Research Summaries:
{research_summaries}

Create a final comprehensive report that:

1. **Executive Summary** (300-500 words)
   - Comprehensive overview of all key findings
   - Main insights and their implications
   - Strategic conclusions and recommendations

2. **Detailed Analysis** (1500-2000 words)
   - In-depth synthesis of findings from all researchers
   - Thorough exploration of patterns, themes, and relationships
   - Detailed resolution of any conflicting information with explanations
   - Deep dive into the most important insights with context
   - Multiple perspectives and viewpoints where relevant

3. **Supporting Evidence** (500-800 words)
   - Extensive key excerpts and quotes with analysis
   - Complete source citations with credibility assessment
   - Statistical data, factual support, and empirical evidence
   - Case studies or examples where applicable

4. **Implications and Applications** (400-600 words)
   - Practical applications of the findings
   - Impact on relevant fields or industries
   - Potential future developments

5. **Conclusions and Recommendations** (500-700 words)
   - Comprehensive conclusions with detailed reasoning
   - Strategic implications and significance
   - Specific, actionable recommendations
   - Areas for further investigation with proposed methodologies
   - Limitations of current research and potential solutions

Ensure the report is extensive, detailed, and thoroughly explores all aspects of the research. Provide rich context, multiple examples, and comprehensive analysis throughout. The final report should be at least 3000 words."""
    }
    
    # Korean prompts
    KO_PROMPTS = {
        "clarification": """당신은 연구 목표와 요구사항을 명확히 하는 전문가입니다.

사용자가 제출한 연구 질문: {research_question}

이 질문을 분석하고 명확화가 필요한지 또는 바로 연구를 진행할 수 있는지 판단하세요.

고려사항:
1. 연구 범위가 명확하고 잘 정의되어 있는가?
2. 명확화가 필요한 모호한 용어가 있는가?
3. 어떤 구체적인 측면을 연구해야 하는가?
4. 어떤 유형의 소스가 가장 가치 있을까?

질문이 충분히 명확하고 구체적이라면 다음과 같이 응답하세요:
"PROCEED_TO_RESEARCH"

명확화가 필요하다면, 필요한 구체적인 정보에 대한 명확한 요청을 제공하세요.""",

        "research_brief": """당신은 연구 계획 전문가입니다. 다음의 명확화된 연구 목표를 바탕으로 포괄적인 연구 계획서를 작성하세요:

연구 목표: {clarified_research_goal}

다음을 포함하는 세부적인 연구 계획서를 작성하세요:

1. **연구 개요**
   - 연구 목적의 명확한 진술
   - 연구의 범위와 경계

2. **핵심 연구 질문들** (연구를 안내할 3-5개의 구체적인 질문)
   - 주요 연구 질문
   - 심층 조사를 위한 부차적 질문

3. **연구 방법론**
   - 우선순위를 두어야 할 소스 유형
   - 연구 접근법 및 전략
   - 정보 품질 기준

4. **기대 성과물**
   - 최종 보고서의 구조
   - 포함해야 할 핵심 섹션
   - 깊이 및 형식 기대치

여러 연구원이 독립적으로 작업하면서도 일관성을 유지할 수 있을 정도로 포괄적인 계획서를 만드세요.""",

        "supervisor": """당신은 연구 프로젝트의 다양한 측면에서 작업하는 여러 연구원을 조율하는 연구 감독자입니다.

연구 계획서: {research_brief}

이 연구를 병렬로 작업하는 개별 연구원에게 할당할 수 있는 구체적이고 집중된 연구 과제로 나누는 것이 당신의 임무입니다.

각각 다음을 포함하는 2-5개의 연구 과제를 생성하세요:
1. **연구 질문**: 구체적이고 집중된 질문
2. **설명**: 이 연구 과제의 세부 범위와 기대사항

각 과제는 다음과 같아야 합니다:
- 독립적이고 자체 완결적
- 전체 연구의 뚜렷한 측면을 다룸
- 단일 연구원이 완료 가능
- 최종 보고서에 의미 있는 기여

응답을 연구 과제의 JSON 목록 형식으로 작성하세요:
[
    {{
        "research_question": "여기에 구체적인 질문",
        "description": "여기에 세부 설명"
    }}
]""",

        "researcher": """당신은 특정 주제에 대한 집중적인 연구를 수행하는 전문 연구원입니다.

연구 과제: {research_question}
설명: {description}

지시사항:
1. 할당된 주제에 대해 철저한 연구를 수행하세요
2. 웹 검색을 사용하여 최신의 권위 있는 정보를 수집하세요
3. 찾은 정보를 분석하고 종합하세요
4. 사실적이고 잘 뒷받침된 정보에 집중하세요
5. 핵심 통찰력과 중요한 세부사항을 식별하세요

당신의 연구는 다음을 포함해야 합니다:
- 할당된 주제의 포괄적인 다룸
- 핵심 발견사항과 통찰력
- 중요한 발췌문과 인용문
- 소스 인용
- 명확하고 잘 조직된 정보

체계적으로 연구를 수행하고 세부적인 발견사항을 제공하세요.""",

        "compression": """당신은 연구 종합 전문가입니다. 여러 연구 요약을 일관되고 포괄적인 보고서로 통합하는 것이 당신의 임무입니다.

개별 연구 요약들:
{research_summaries}

다음을 포함하는 최종 종합 보고서를 작성하세요:

1. **요약**
   - 핵심 발견사항 개요
   - 주요 통찰력과 결론

2. **상세 분석**
   - 모든 연구원의 발견사항 종합
   - 패턴과 주제 식별
   - 상충하는 정보 해결
   - 가장 중요한 통찰력 강조

3. **뒷받침하는 증거**
   - 핵심 발췌문과 인용문
   - 소스 인용
   - 통계적 또는 사실적 지원

4. **결론**
   - 연구에 기반한 명확한 결론
   - 함의와 중요성
   - 관련이 있다면 추가 조사 영역

중복을 피하면서 잘 조직되고 일관성 있으며 포괄적인 보고서를 보장하세요."""
    }
    
    @classmethod
    def get_prompt(cls, template_name: str, language: LanguageCode, **kwargs) -> str:
        """Get localized prompt template with variables filled in."""
        prompts = cls.KO_PROMPTS if language == "ko" else cls.EN_PROMPTS
        template = prompts.get(template_name, cls.EN_PROMPTS.get(template_name, ""))
        
        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required variable {e} for prompt template '{template_name}'")
    
    @classmethod
    def get_available_templates(cls) -> list[str]:
        """Get list of available prompt templates."""
        return list(cls.EN_PROMPTS.keys())
    
    @classmethod
    def validate_template_vars(cls, template_name: str, variables: Dict[str, Any]) -> bool:
        """Validate that all required variables are provided for a template."""
        template = cls.EN_PROMPTS.get(template_name, "")
        if not template:
            return False
        
        # Extract variable names from template
        import re
        required_vars = set(re.findall(r'\{(\w+)\}', template))
        provided_vars = set(variables.keys())
        
        return required_vars.issubset(provided_vars)