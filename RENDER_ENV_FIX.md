# Render 환경 변수 추가 - UTF-8 인코딩 수정

## 문제:
```
ERROR 500: 'cp949' codec can't encode character '\u2554'
```

## 해결 방법:

### Render 대시보드에서:

1. 서비스 클릭
2. **Environment** 탭 클릭
3. **"Add Environment Variable"** 클릭
4. 다음 변수 추가:

```
Key: PYTHONIOENCODING
Value: utf-8
```

5. **"Save Changes"** 클릭
6. 자동으로 재배포됩니다 (1-2분 소요)

---

## 또는 이미 있는 변수:

만약 이미 있다면:
```
Key: LANG
Value: en_US.UTF-8
```

또는:
```
Key: LC_ALL
Value: en_US.UTF-8
```

---

## 확인:

재배포 완료 후 다시 테스트:
```bash
python test_render_api.py
```

이제 500 에러가 사라지고 정상 작동할 겁니다!
