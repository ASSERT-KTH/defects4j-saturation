Repair a real defect in the Java project Closure (Defects4J bug Closure-127).

The working directory is a checkout of the buggy version. Layout:
  - production sources : src
  - test sources       : test   (read-only for you)

The sources currently compile. The following developer test(s) fail because of
the defect:

  - com.google.javascript.jscomp.UnreachableCodeEliminationTest::testIssue4177428_return
  - com.google.javascript.jscomp.UnreachableCodeEliminationTest::testDontRemoveBreakInTryFinally
  - com.google.javascript.jscomp.UnreachableCodeEliminationTest::testIssue4177428_continue
  - com.google.javascript.jscomp.UnreachableCodeEliminationTest::testDontRemoveBreakInTryFinallySwitch
  - com.google.javascript.jscomp.UnreachableCodeEliminationTest::testIssue4177428a
  - com.google.javascript.jscomp.UnreachableCodeEliminationTest::testIssue4177428c

Failure output from the initial test run:

```
--- com.google.javascript.jscomp.UnreachableCodeEliminationTest::testIssue4177428_return
junit.framework.AssertionFailedError: 
Expected: f=function(){var action;a:{var proto=null;try{proto=new Proto}finally{action=proto;return}}}
Result: f=function(){var action;a:{var proto=null;try{proto=new Proto}finally{action=proto}}}
Node tree inequality:
Tree1:
BLOCK [synthetic: 1]
    SCRIPT 1 [synthetic: 1] [source_file: expected0] [input_id: InputId: expected0]
        EXPR_RESULT 1 [source_file: expected0]
            ASSIGN 1 [source_file: expected0]
                NAME f 1 [source_file: expected0]
                FUNCTION  1 [source_file: expected0]
                    NAME  1 [source_file: expected0]
                    PARAM_LIST 1 [source_file: expected0]
                    BLOCK 1 [source_file: expected0]
                        VAR 2 [source_file: expected0]
                            NAME action 2 [source_file: expected0]
                        LABEL 3 [source_file: expected0]
                            LABEL_NAME a 3 [source_file: expected0]
                            BLOCK 3 [source_file: expected0]
                                VAR 4 [source_file: expected0]
                                    NAME proto 4 [source_file: expected0]
                                        NULL 4 [source_file: expected0]
                                TRY 5 [source_file: expected0]
                                    BLOCK 5 [source_file: expected0]
                                        EXPR_RESULT 6 [source_file: expected0]
                                            ASSIGN 6 [source_file: expected0]
                                                NAME proto 6 [source_file: expected0]
                                                NEW 6 [source_file: expected0]
                                                    NAME Proto 6 [source_file: expected0]
                                    BLOCK 7 [source_file: expected0]
                                    BLOCK 7 [source_file: expected0]
                                        EXPR_RESULT 8 [source_file: expected0]
                                            ASSIGN 8 [source_file: expected0]
                                                NAME action 8 [source_file: expected0]
                                                NAME proto 8 [source_file: expected0]
                                        RETURN 9 [source_file: expected0]


Tree2:
BLOCK [synthetic: 1]
    SCRIPT 1 [synthetic: 1] [source_file: testcode] [input_id: InputId: testcode]
        EXPR_RESULT 1 [source_file: testcode]
            ASSIGN 1 [source_file: testcode]
                NAME f 1 [source_file: testcode]
                FUNCTION  1 [source_file: testcode]
                    NAME  1 [source_file: testcode]
                    PARAM_LIST 1 [source_file: testcode]
                    BLOCK 1 [source_file: testcode]
                        VAR 2 [source_file: testcode]
                            NAME action 2 [source_file: testcode]
                        LABEL 3 [source_file: testcode]
                            LABEL_NAME a 3 [source_file: testcode]
                            BLOCK 3 [source_file: testcode]
                                VAR 4 [source_file: testcode]
                                    NAME proto 4 [source_file: testcode]
                                        NULL 4 [source_file: testcode]
                                TRY 5 [source_file: testcode]
                                    BLOCK 5 [source_file: testcode]
                                        EXPR_RESULT 6 [source_file: testcode]
                                            ASSIGN 6 [source_file: testcode]
                                                NAME proto 6 [source_file: testcode]
                                                NEW 6 [source_file: testcode]
                                                    NAME Proto 6 [source_file: testcode]
                                    BLOCK 7 [source_file: testcode]
                                    BLOCK 7 [source_file: testcode]
                                        EXPR_RESULT 8 [source_file: testcode]
                                            ASSIGN 8 [source_file: testcode]
                                                NAME action 8 [source_file: testcode]
                                                NAME proto 8 [source_file: testcode]


Subtree1: BLOCK 7 [source_file: expected0]
    EXPR_RESULT 8 [source_file: expected0]
        ASSIGN 8 [source_file: expected0]
            NAME action 8 [source_file: expected0]
            NAME proto 8 [source_file: expected0]
    RETURN 9 [source_file: expected0]


Subtree2: BLOCK 7 [source_file: testcode]
    EXPR_RESULT 8 [source_file: testcode]
        ASSIGN 8 [source_file: testcode]
            NAME action 8 [source_file: testcode]
            NAME proto 8 [source_file: testcode]

	at junit.framework.Assert.fail(Assert.java:57)
	at junit.framework.Assert.assertTrue(Assert.java:22)
	at junit.framework.Assert.assertNull(Assert.java:277)
	at junit.framework.TestCase.assertNull(TestCase.java:447)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:928)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:460)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:386)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:355)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:343)
	at com.google.javascript.jscomp.UnreachableCodeEliminationTest.testIssue4177428_return(UnreachableCodeEliminationTest.java:362)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:62)
	at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
	at java.base/java.lang.reflect.Method.invoke(Method.java:566)
	at junit.framework.TestCase.runTest(TestCase.java:176)
	at junit.framework.TestCase.runBare(TestCase.java:141)
	at junit.framework.TestResult$1.protect(TestResult.java:122)
	at junit.framework.TestResult.runProtected(TestResult.java:142)
	at junit.framework.TestResult.run(TestResult.java:125)
	at junit.framework.TestCase.run(TestCase.java:129)
	at junit.framework.TestSuite.runTest(TestSuite.java:252)
	at junit.framework.TestSuite.run(TestSuite.java:247)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTestRunner.run(JUnitTestRunner.java:520)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.executeInVM(JUnitTask.java:1492)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.executeTests(JUnitTask.java:878)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.executeOrQueue(JUnitTask.java:1980)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.executeTests(JUnitTask.java:830)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.execute(JUnitTask.java:2287)
	at org.apache.tools.ant.UnknownElement.execute(UnknownElement.java:291)
	at jdk.internal.reflect.GeneratedMethodAccessor4.invoke(Unknown Source)
	at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
	at java.base/java.lang.reflect.Method.invoke(Method.java:566)
	at org.apache.tools.ant.dispatch.DispatchUtils.execute(DispatchUtils.java:106)
	at org.apache.tools.ant.Task.perform(Task.java:348)
	at org.apache.tools.ant.Target.execute(Target.java:392)
	at org.apache.tools.ant.Target.performTasks(Target.java:413)
	at org.apache.tools.ant.Project.executeSortedTargets(Project.java:1399)
	at org.apache.tools.ant.Project.executeTarget(Project.java:1368)
	at org.apache.tools.ant.helper.DefaultExecutor.executeTargets(DefaultExecutor.java:41)
	at org.apache.tools.ant.Project.executeTargets(Project.java:1251)
	at org.apache.tools.ant.Main.runBuild(Main.java:811)
	at org.apache.tools.ant.Main.startAnt(Main.java:217)
	at org.apache.tools.ant.launch.Launcher.run(Launcher.java:280)
	at org.apache.tools.ant.launch.Launcher.main(Launcher.java:109)
--- com.google.javascript.jscomp.UnreachableCodeEliminationTest::testDontRemoveBreakInTryFinally
junit.framework.AssertionFailedError: 
Expected: function f(){b:try{throw 9;}finally{break b}return 1}
Result: function f(){b:try{throw 9;}finally{}return 1}
Node tree inequality:
Tree1:
BLOCK [synthetic: 1]
    SCRIPT 1 [synthetic: 1] [source_file: expected0] [input_id: InputId: expected0]
        FUNCTION f 1 [source_file: expected0]
            NAME f 1 [source_file: expected0]
            PARAM_LIST 1 [source_file: expected0]
            BLOCK 1 [source_file: expected0]
                LABEL 1 [source_file: expected0]
                    LABEL_NAME b 1 [source_file: expected0]
                    TRY 1 [source_file: expected0]
                        BLOCK 1 [source_file: expected0]
                            THROW 1 [source_file: expected0]
                                NUMBER 9.0 1 [source_file: expected0]
                        BLOCK 1 [source_file: expected0]
                        BLOCK 1 [source_file: expected0]
                            BREAK 1 [source_file: expected0]
                                LABEL_NAME b 1 [source_file: expected0]
                RETURN 1 [source_file: expected0]
                    NUMBER 1.0 1 [source_file: expected0]


Tree2:
BLOCK [synthetic: 1]
    SCRIPT 1 [synthetic: 1] [source_file: testcode] [input_id: InputId: testcode]
        FUNCTION f 1 [source_file: testcode]
            NAME f 1 [source_file: testcode]
            PARAM_LIST 1 [source_file: testcode]
            BLOCK 1 [source_file: testcode]
                LABEL 1 [source_file: testcode]
                    LABEL_NAME b 1 [source_file: testcode]
                    TRY 1 [source_file: testcode]
                        BLOCK 1 [source_file: testcode]
                            THROW 1 [source_file: testcode]
                                NUMBER 9.0 1 [source_file: testcode]
                        BLOCK 1 [source_file: testcode]
                        BLOCK 1 [source_file: testcode]
                RETURN 1 [source_file: testcode]
                    NUMBER 1.0 1 [source_file: testcode]


Subtree1: BLOCK 1 [source_file: expected0]
    BREAK 1 [source_file: expected0]
        LABEL_NAME b 1 [source_file: expected0]


Subtree2: BLOCK 1 [source_file: testcode]

	at junit.framework.Assert.fail(Assert.java:57)
	at junit.framework.Assert.assertTrue(Assert.java:22)
	at junit.framework.Assert.assertNull(Assert.java:277)
	at junit.framework.TestCase.assertNull(TestCase.java:447)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:928)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:460)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:386)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:355)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:343)
	at com.google.javascript.jscomp.CompilerTestCase.testSame(CompilerTestCase.java:582)
	at com.google.javascript.jscomp.UnreachableCodeEliminationTest.testDontRemoveBreakInTryFinally(UnreachableCodeEliminationTest.java:417)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:62)
	at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
	at java.base/java.lang.reflect.Method.invoke(Method.java:566)
	at junit.framework.TestCase.runTest(TestCase.java:176)
	at junit.framework.TestCase.runBare(TestCase.java:141)
	at junit.framework.TestResult$1.protect(TestResult.java:122)
	at junit.framework.TestResult.runProtected(TestResult.java:142)
	at junit.framework.TestResult.run(TestResult.java:125)
	at junit.framework.TestCase.run(TestCase.java:129)
	at junit.framework.Tes
... (truncated)
```

Your task: find the root cause and fix it in src, then verify with
`defects4j compile` and `defects4j test` that the failing test(s) pass and that
no other developer test broke.
