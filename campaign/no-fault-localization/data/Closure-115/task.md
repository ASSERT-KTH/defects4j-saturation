Repair a real defect in the Java project Closure (Defects4J bug Closure-115).

The working directory is a checkout of the buggy version. Layout:
  - production sources : src
  - test sources       : test   (read-only for you)

The sources currently compile. The following developer test(s) fail because of
the defect:

  - com.google.javascript.jscomp.InlineFunctionsTest::testBug4944818
  - com.google.javascript.jscomp.InlineFunctionsTest::testDoubleInlining1
  - com.google.javascript.jscomp.InlineFunctionsTest::testNoInlineIfParametersModified8
  - com.google.javascript.jscomp.InlineFunctionsTest::testNoInlineIfParametersModified9
  - com.google.javascript.jscomp.InlineFunctionsTest::testInlineFunctions6

Failure output from the initial test run:

```
--- com.google.javascript.jscomp.InlineFunctionsTest::testBug4944818
junit.framework.AssertionFailedError: 
Expected: HangoutStarter.prototype.launchHangout=function(){var self$$2=a.b;var JSCompiler_temp_const$$0=goog.Uri;var JSCompiler_inline_result$$1;var self$$inline_2=self$$2;if(!self$$inline_2.domServices_)self$$inline_2.domServices_=goog$component$DomServices.get(self$$inline_2.appContext_);JSCompiler_inline_result$$1=self$$inline_2.domServices_;var myUrl=new JSCompiler_temp_const$$0(JSCompiler_inline_result$$1.getDomHelper().getWindow().location.href)}
Result: HangoutStarter.prototype.launchHangout=function(){var self$$2=a.b;var JSCompiler_temp_const$$0=goog.Uri;var JSCompiler_inline_result$$1;var JSCompiler_inline_result$$0;var self$$inline_1=self$$2;if(!self$$inline_1.domServices_)self$$inline_1.domServices_=goog$component$DomServices.get(self$$inline_1.appContext_);JSCompiler_inline_result$$0=self$$inline_1.domServices_;JSCompiler_inline_result$$1=JSCompiler_inline_result$$0.getDomHelper().getWindow();var myUrl=new JSCompiler_temp_const$$0(JSCompiler_inline_result$$1.location.href)}
Node tree inequality:
Tree1:
BLOCK [synthetic: 1]
    SCRIPT 1 [synthetic: 1] [source_file: expected0] [input_id: InputId: expected0]
        EXPR_RESULT 1 [source_file: expected0]
            ASSIGN 1 [source_file: expected0]
                GETPROP 1 [source_file: expected0]
                    GETPROP 1 [source_file: expected0]
                        NAME HangoutStarter 1 [source_file: expected0]
                        STRING prototype 1 [source_file: expected0]
                    STRING launchHangout 1 [source_file: expected0]
                FUNCTION  1 [source_file: expected0]
                    NAME  1 [source_file: expected0]
                    PARAM_LIST 1 [source_file: expected0]
                    BLOCK 1 [source_file: expected0]
                        VAR 1 [source_file: expected0]
                            NAME self$$2 1 [source_file: expected0]
                                GETPROP 1 [source_file: expected0]
                                    NAME a 1 [source_file: expected0]
                                    STRING b 1 [source_file: expected0]
                        VAR 1 [source_file: expected0]
                            NAME JSCompiler_temp_const$$0 1 [source_file: expected0]
                                GETPROP 1 [source_file: expected0]
                                    NAME goog 1 [source_file: expected0]
                                    STRING Uri 1 [source_file: expected0]
                        VAR 1 [source_file: expected0]
                            NAME JSCompiler_inline_result$$1 1 [source_file: expected0]
                        BLOCK 1 [source_file: expected0]
                            VAR 1 [source_file: expected0]
                                NAME self$$inline_2 1 [source_file: expected0]
                                    NAME self$$2 1 [source_file: expected0]
                            IF 1 [source_file: expected0]
                                NOT 1 [source_file: expected0]
                                    GETPROP 1 [source_file: expected0]
                                        NAME self$$inline_2 1 [source_file: expected0]
                                        STRING domServices_ 1 [source_file: expected0]
                                BLOCK 1 [source_file: expected0]
                                    EXPR_RESULT 1 [source_file: expected0]
                                        ASSIGN 1 [source_file: expected0]
                                            GETPROP 1 [source_file: expected0]
                                                NAME self$$inline_2 1 [source_file: expected0]
                                                STRING domServices_ 1 [source_file: expected0]
                                            CALL 1 [source_file: expected0]
                                                GETPROP 1 [source_file: expected0]
                                                    NAME goog$component$DomServices 1 [source_file: expected0]
                                                    STRING get 1 [source_file: expected0]
                                                GETPROP 1 [source_file: expected0]
                                                    NAME self$$inline_2 1 [source_file: expected0]
                                                    STRING appContext_ 1 [source_file: expected0]
                            EXPR_RESULT 1 [source_file: expected0]
                                ASSIGN 1 [source_file: expected0]
                                    NAME JSCompiler_inline_result$$1 1 [source_file: expected0]
                                    GETPROP 1 [source_file: expected0]
                                        NAME self$$inline_2 1 [source_file: expected0]
                                        STRING domServices_ 1 [source_file: expected0]
                        VAR 1 [source_file: expected0]
                            NAME myUrl 1 [source_file: expected0]
                                NEW 1 [source_file: expected0]
                                    NAME JSCompiler_temp_const$$0 1 [source_file: expected0]
                                    GETPROP 1 [source_file: expected0]
                                        GETPROP 1 [source_file: expected0]
                                            CALL 1 [source_file: expected0]
                                                GETPROP 1 [source_file: expected0]
                                                    CALL 1 [source_file: expected0]
                                                        GETPROP 1 [source_file: expected0]
                                                            NAME JSCompiler_inline_result$$1 1 [source_file: expected0]
                                                            STRING getDomHelper 1 [source_file: expected0]
                                                    STRING getWindow 1 [source_file: expected0]
                                            STRING location 1 [source_file: expected0]
                                        STRING href 1 [source_file: expected0]


Tree2:
BLOCK [synthetic: 1]
    SCRIPT 1 [synthetic: 1] [source_file: testcode] [input_id: InputId: testcode]
        EXPR_RESULT 13 [source_file: testcode]
            ASSIGN 13 [source_file: testcode]
                GETPROP 13 [source_file: testcode]
                    GETPROP 13 [source_file: testcode]
                        NAME HangoutStarter 13 [source_file: testcode]
                        STRING prototype 13 [source_file: testcode]
                    STRING launchHangout 13 [source_file: testcode]
                FUNCTION  13 [source_file: testcode]
                    NAME  13 [source_file: testcode]
                    PARAM_LIST 13 [source_file: testcode]
                    BLOCK 13 [source_file: testcode]
                        VAR 14 [source_file: testcode]
                            NAME self$$2 14 [source_file: testcode]
                                GETPROP 14 [source_file: testcode]
                                    NAME a 14 [source_file: testcode]
                                    STRING b 14 [source_file: testcode]
                        VAR 15 [source_file: testcode]
                            NAME JSCompiler_temp_const$$0 15 [source_file: testcode]
                                GETPROP 15 [source_file: testcode]
                                    NAME goog 15 [source_file: testcode]
                                    STRING Uri 15 [source_file: testcode]
                        VAR 15 [source_file: testcode]
                            NAME JSCompiler_inline_result$$1 15 [source_file: testcode]
                        BLOCK 9 [source_file: testcode]
                            VAR 10 [source_file: testcode]
                                NAME JSCompiler_inline_result$$0 10 [source_file: testcode]
                            BLOCK 1 [source_file: testcode]
                                VAR 15 [source_file: testcode]
                                    NAME self$$inline_1 15 [source_file: testcode]
                                        NAME self$$2 15 [source_file: testcode]
                                IF 2 [source_file: testcode]
                                    NOT 2 [source_file: testcode]
                                        GETPROP 2 [source_file: testcode]
                                            NAME self$$inline_1 2 [source_file: testcode]
                                            STRING domServices_ 2 [source_file: testcode]
                                    BLOCK 2 [source_file: testcode]
                                        EXPR_RESULT 3 [source_file: testcode]
                                            ASSIGN 3 [source_file: testcode]
                                                GETPROP 3 [source_file: testcode]
                                                    NAME self$$inline_1 3 [source_file: testcode]
                                                    STRING domServices_ 3 [source_file: testcode]
                                                CALL 3 [source_file: testcode]
                                                    GETPROP 3 [source_file: testcode]
                                                        NAME goog$component$DomServices 3 [source_file: testcode]
                                                        STRING get 3 [source_file: testcode]
                                                    GETPROP 3 [source_file: testcode]
                                                        NAME self$$inline_1 3 [source_file: testcode]
                                                        STRING appContext_ 3 [source_file: testcode]
                                EXPR_RESULT 6 [source_file: testcode]
                                    ASSIGN 6 [source_file: testcode]
                                        NAME JSCompiler_inline_result$$0 6 [source_file: testcode]
                                        GETPROP 6 [source_file: testcode]
                                            NAME self$$inline_1 6 [source_file: testcode]
                                            STRING domServices_ 6 [source_file: testcode]
                            EXPR_RESULT 10 [source_file: testcode]
                                ASSIGN 10 [source_file: testcode]
                                    NAME JSCompiler_inline_result$$1 10 [source_file: testcode]
                                    CALL 10 [source_file: testcode]
                                        GETPROP 10 [source_file: testcode]
                                            CALL 10 [source_file: testcode]
                                                GETPROP 10 [source_file: testcode]
                                                    NAME JSCompiler_inline_result$$0 10 [source_file: testcode]
                                                    STRING getDomHelper 10 [source_file: testcode]
                                            STRING getWindow 10 [source_file: testcode]
                        VAR 15 [source_file: testcode]
                            NAME myUrl 15 [source_file: testcode]
                                NEW 15 [source_file: testcode]
                                    NAME JSCompiler_temp_const$$0 15 [source_file: testcode]
                                    GETPROP 15 [source_file: testcode]
                                        GETPROP 15 [source_file: testcode]
                                            NAME JSCompiler_inline_result$$1 15 [source_file: testcode]
                                            STRING location 15 [source_file: testcode]
                                        STRING href 15 [source_file: testcode]


Subtree1: NAME self$$inline_2 1 [source_file: expected0]
    NAME self$$2 1 [source_file: expected0]


Subtree2: NAME JSCompiler_inline_result$$0 10 [source_file: testcode]

	at junit.framework.Assert.fail(A
... (truncated)
```

Your task: find the root cause and fix it in src, then verify with
`defects4j compile` and `defects4j test` that the failing test(s) pass and that
no other developer test broke.
