# 주식동향예측조 캡스톤 디자인 repository

## 1. 조원 및 역할

- 김세훈: 시스템 메인 로직 설계/구현
- 서범창: 웹 프론트엔드 디자인 설계/구현
- 김태균: 웹 벡엔드/DB 설계/구현

## 2. 현재 프로젝트에서 사용중인 python 라이브러리

- 아래 라이브러리들은 해당 프로젝트 개발 및 테스팅에 필수적인 라이브러리 입니다.

1. pandas
2. pandas-datareader (yahoo finance 데이터 크롤링에 필요합니다.)
3. Django
4. matplotlib
5. chart.js
6. csv(csv 리더 등)

## 3. 프로젝트 구조
```buildoutcfg

├─capstone_project
│  │
│  ├─accounts                                               - 계정 관련 기능 모듈
│  │   ├─static                                             - frontend 자원들 저장
│  │   │   ├─css
│  │   │   └─js
│  │   └─templates                                          - accounts 앱에 사용되는 html파일 저장
│  │       └─accounts   
│  │
│  ├─capstone_project                                       - 프로젝트 전체 관리 모듈
│  │
│  ├─main
│  │   ├─data                                               - data파일 저장용
│  │   │  └─company_list                                    - 회사 이름 및 코드 데이터 저장 디렉토리
│  │   ├─static
│  │   │  ├─css                                             - css파일 저장
│  │   │  ├─images                                          - frontend 이미지 저장
│  │   │  └─js                                              - javascript파일 저장
│  │   └─templates
│  │      └─capstone_project                                - main앱에 사용되는 html파일 저장
│  └─templates                                              - base html파일 저장(템플릿 확장용)
│
└─venv                                                      - 가상 환경 파일들

```

## 4. 라이센스
- 해당 웹 어플리케이션 라이센스는 MIT 라이센스입니다



