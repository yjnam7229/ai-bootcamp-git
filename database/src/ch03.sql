/*Ch03 예제*/

/*예제3-1*/
SELECT CHAR_LENGTH('HELLO')
      ,LENGTH('HELLO')
      ,CHAR_LENGTH('안녕')
      ,LENGTH('안녕');

/*예제3-2*/
SELECT CONCAT('DREAMS', 'COME', 'TRUE')
      ,CONCAT_WS('-', '2023', '01', '29');

/*예제3-3*/
SELECT LEFT('SQL 완전정복', 3)
      ,RIGHT('SQL 완전정복', 4)
      ,SUBSTR('SQL 완전정복', 2, 5) 
      ,SUBSTR('SQL 완전정복', 2); 

/*예제3-4*/
/*문자열, 구분자, 인덱스 */
SELECT SUBSTRING_INDEX('서울시 동작구 흑석로', ' ', 2) 
      ,SUBSTRING_INDEX('서울시 동작구 흑석로', ' ', -2);

/*예제3-5*/
SELECT LPAD('SQL', 10, '#')
      ,RPAD('SQL', 5, '*');

/*예제3-6*/
/*TRIM 특정 문자열이 앞뒤로 빈여백의 포함여부를 체크해서 이를 제거해주는 함수*/
SELECT LENGTH(LTRIM(' SQL '))
      ,LENGTH(RTRIM(' SQL '))
      ,LENGTH(TRIM(' SQL ')); 

/*예제3-7*/
SELECT TRIM(BOTH 'abc' FROM 'abcSQLabcabc')
      ,TRIM(LEADING 'abc' FROM 'abcSQLabcabc') /*LEADING 왼쪽 문자열 제거*/
      ,TRIM(TRAILING 'abc' FROM 'abcSQLabcabc'); /*TRAILING 오른쪽 문자열 제거*/

/*예제3-8*/
/*찾고자 하는 문자열, 문자열 열거*/
SELECT FIELD('JAVA', 'SQL', 'JAVA', 'C') /*찾고자 하는 문자열의 인덱스 위치*/
      ,FIND_IN_SET('JAVA', 'SQL,JAVA,C') /*문자열 내에서 지정한 문자의 위치*/
      ,INSTR('네 인생을 살아라', '인생') /*기준문자열에서 검색 문자열을 찾아 인덱스 반환*/
      ,LOCATE('인생', '네 인생을 살아라'); /*INSTR() 반대*/

/*예제3-9*/
SELECT ELT(2, 'SQL', 'JAVA', 'C'); /*검색하고자 하는 인덱스 위치값*/

/*예제3-10*/
SELECT REPEAT('*', 5);

/*예제3-11*/
SELECT REPLACE('010.1234.5678', '.', '-');

/*예제3-12*/
SELECT REVERSE('OLLEH');

/*예제3-13*/
SELECT CEILING(123.56)
      ,FLOOR(123.56)
      ,ROUND(123.56)
      ,ROUND(123.56, 1)
      ,TRUNCATE(123.56, 1);

/*예제3-14*/
SELECT ABS(-120)
      ,ABS(120)
      ,SIGN(-120)
      ,SIGN(120);

/*예제3-15*/
SELECT MOD(203, 4)
      ,203 % 4
      ,203 MOD 4;

/*예제3-16*/
SELECT POWER(2, 3) /*승*/
      ,SQRT(16) /*제곱근*/
      ,RAND() /*랜덤함수*/
      ,RAND(100)
      ,ROUND(RAND() * 100);

/*예제3-17*/
SELECT NOW()
      ,SYSDATE()
      ,CURDATE()
      ,CURTIME();

/*예제3-18*/
SELECT NOW()
      ,YEAR(NOW())
      ,QUARTER(NOW()) /*현재 날짜 시간을 기준으로 분기를 리턴*/
      ,MONTH(NOW())
      ,DAY(NOW())
      ,HOUR(NOW())
      ,MINUTE(NOW())
      ,SECOND(NOW());

/*예제3-19*/
SELECT NOW()
      ,DATEDIFF('2025-12-20', NOW()) /*기준날짜, 실행하는 시점의 시간정보, 날짜 차이 반환*/ 
      ,DATEDIFF(NOW(), '2025-12-20')
      ,TIMESTAMPDIFF(YEAR, NOW(), '2025-12-20')
      ,TIMESTAMPDIFF(MONTH, NOW(), '2025-12-20')
      ,TIMESTAMPDIFF(DAY, NOW(), '2025-12-20');
      
/*예제3-20*/
SELECT NOW()
      ,ADDDATE(NOW(), 50)
      ,ADDDATE(NOW(), INTERVAL 50 DAY)
      ,ADDDATE(NOW(), INTERVAL 50 MONTH)
      ,SUBDATE(NOW(), INTERVAL 50 HOUR);

/*예제3-21*/
/*오늘 날짜를 기준으로 이번달 마지막 날짜, 일 년 중 몇 일째인지, 월이름과 요일 확인*/
SELECT NOW()
      ,LAST_DAY(NOW())
      ,DAYOFYEAR(NOW())
      ,MONTHNAME(NOW())
      ,WEEKDAY(NOW());

/*예제3-22*/
/*형변환 함수*/
SELECT CAST('1' AS UNSIGNED)
      ,CAST(2 AS CHAR(1))
      ,CONVERT('1', UNSIGNED) /*문자->숫자, 숫자->문자*/
      ,CONVERT(2, CHAR(1));

/*예제3-23*/
/*제어흐름 함수*/
SELECT IF(12500 * 450 > 5000000, '초과달성', '미달성');

/*예제3-24*/
SELECT IFNULL(1, 0) /*수식1이 NULL 아니면 1을 반환*/
      ,IFNULL(NULL, 0)
      ,IFNULL(1/0, 'OK');

/*예제3-25*/
SELECT NULLIF(12 * 10, 120)
      ,NULLIF(12 * 10, 1200);

/*예제3-26*/
SELECT CASE 
            WHEN 12500 * 450 > 5000000 THEN '초과달성'
            WHEN 12500 * 450 > 4000000 THEN '달성'
            ELSE '미달성'
       END;