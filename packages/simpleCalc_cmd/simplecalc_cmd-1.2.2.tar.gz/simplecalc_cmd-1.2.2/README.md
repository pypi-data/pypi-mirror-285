# 첫번째 팀프로젝트

## Goals
- 2명씩 조를 이루어 pip package 를 만들기
- 조 이름으로 팩키지를 만들기
- 간단한 계산기 기능(함수단위)을 만들기
- calc 파일에 간단한 계산기 구현 후 pip에 배포 
- cmd파일을 만들어 calc의 패키지를 설치하고 dependencies에 추가

- 실행 

## Install

```
$ pip install simpleCalc_cmd
```

## Mechanism
`hc_add`, `hc_mul`, `hc_div` 패키지를 dependency로 가지고 있으며 해당 패키지들의 `add`, `div`, `mul` 함수를 통해 `call_add`, `call_div`, `call_mul`을 구현하고 있습니다.

해당 함수들은 command line에서 `hc_add`, `hc_div`, `hc_mul`의 세가지 커맨드로 호출되며, 각각 정수 형태의 in-line arguements를 2개 요구합니다. 

나눗셈을 구현하는 `hc_div`의 경우 결과값을 `몫 remainder 나머지` 형태로 출력합니다.

## Example
```
$ hc_add 1 3
4

$hc_div 10 3
3 remainder 3

$hc_mul 3 3
9
```

## Urls
- Github : https://github.com/hamsunwoo/simpleCalc_cmd
