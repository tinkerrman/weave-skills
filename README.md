# Weave Skills

W&B Weave를 위한 Claude Code 스킬입니다. LLM 관측성(observability)과 평가(evaluation)를 쉽게 구현할 수 있도록 도와줍니다.

[English](README.en.md)

## 설치 방법

### 방법 1: 플러그인 마켓플레이스 (권장)

```bash
# 마켓플레이스 등록
/plugin marketplace add https://github.com/YOUR_USERNAME/weave-skills

# 플러그인 설치
/plugin install weave
```

### 방법 2: 프로젝트에 복사

```bash
# 프로젝트 디렉토리에 스킬 복사
cp -r skills/weave .claude/skills/
```

### 방법 3: 글로벌 스킬

```bash
# 홈 디렉토리에 스킬 복사 (모든 프로젝트에서 사용 가능)
cp -r skills/weave ~/.claude/skills/
```

## 제공 기능

`/weave` 스킬은 다음 기능을 제공합니다:

| 기능 | 설명 | 키워드 |
|------|------|--------|
| **init** | Weave 프로젝트 초기화 | init, initialize, setup |
| **add-tracing** | 함수에 트레이싱 추가 | trace, tracing, @weave.op |
| **create-scorer** | 평가용 Scorer 생성 | scorer, score, judge |
| **create-eval** | 평가 파이프라인 구성 | eval, evaluation, pipeline |
| **create-dataset** | 평가 데이터셋 생성 | dataset, data, csv |

## 사용 예시

### 명시적 요청

```
사용자: "weave 초기화해줘"
사용자: "LLM 호출 함수에 트레이싱 추가해줘"
사용자: "관련성 평가하는 scorer 만들어줘"
```

### 모호한 요청

```
사용자: "weave 설정해줘"
Claude: 코드베이스를 분석하고 필요한 기능을 추천합니다.
```

### 분석 요청

```
사용자: "weave 상태 확인해줘"
Claude: 현재 상태를 분석하고 보고합니다 (파일 수정 없음).
```

## 디렉토리 구조

```
weave-skills/
├── .claude-plugin/
│   └── marketplace.json      # 마켓플레이스 등록용
├── plugins/weave/            # 독립 플러그인 패키지
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── skills/weave/
│   │   └── SKILL.md
│   ├── assets/
│   └── references/
├── skills/weave/             # 메인 스킬 정의
│   ├── SKILL.md              # 라우터 스킬
│   ├── assets/               # 코드 예시
│   └── references/           # 상세 가이드
├── demo/
│   └── rag-qa/               # 데모 프로젝트
├── CLAUDE.md
└── README.md
```

## 데모

[demo/rag-qa](demo/rag-qa) 폴더에서 스킬 적용 예시를 확인할 수 있습니다.

## Weave 관련 링크

- [Weave 공식 문서](https://docs.wandb.ai/weave)
- [Weave GitHub](https://github.com/wandb/weave)
- [W&B 대시보드](https://wandb.ai/weave)

## 라이선스

MIT License
