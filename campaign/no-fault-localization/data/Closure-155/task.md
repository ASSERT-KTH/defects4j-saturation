Repair a real defect in the Java project Closure (Defects4J bug Closure-155).

The working directory is a checkout of the buggy version. Layout:
  - production sources : src
  - test sources       : test   (read-only for you)

The sources currently compile. The following developer test(s) fail because of
the defect:

  - com.google.javascript.jscomp.InlineVariablesTest::testArgumentsModifiedInInnerFunction
  - com.google.javascript.jscomp.InlineVariablesTest::testArgumentsModifiedInOuterFunction
  - com.google.javascript.jscomp.InlineVariablesTest::testIssue378ModifiedArguments1
  - com.google.javascript.jscomp.InlineVariablesTest::testIssue378ModifiedArguments2
  - com.google.javascript.jscomp.InlineVariablesTest::testIssue378EscapedArguments1
  - com.google.javascript.jscomp.InlineVariablesTest::testIssue378EscapedArguments2
  - com.google.javascript.jscomp.InlineVariablesTest::testIssue378EscapedArguments4

Failure output from the initial test run:

```
--- com.google.javascript.jscomp.InlineVariablesTest::testArgumentsModifiedInInnerFunction
junit.framework.AssertionFailedError: 
Expected: function g(callback){function inner(callback$$1){var x=callback$$1;arguments[0]=this;x.apply(this)}callback.apply(this,arguments)}
Result: function g(callback){function inner(callback$$1){arguments[0]=this;callback$$1.apply(this)}callback.apply(this,arguments)}
Node tree inequality:
Tree1:
BLOCK [synthetic: 1]
    SCRIPT 1 [sourcename: expected0] [synthetic: 1]
        FUNCTION g 1 [sourcename: expected0]
            NAME g 1 [sourcename: expected0]
            LP 1 [sourcename: expected0]
                NAME callback 1 [sourcename: expected0]
            BLOCK 1 [sourcename: expected0]
                FUNCTION inner 3 [sourcename: expected0]
                    NAME inner 3 [sourcename: expected0]
                    LP 3 [sourcename: expected0]
                        NAME callback$$1 3 [sourcename: expected0]
                    BLOCK 3 [sourcename: expected0]
                        VAR 3 [sourcename: expected0]
                            NAME x 3 [sourcename: expected0]
                                NAME callback$$1 3 [sourcename: expected0]
                        EXPR_RESULT 4 [sourcename: expected0]
                            ASSIGN 4 [sourcename: expected0]
                                GETELEM 4 [sourcename: expected0]
                                    NAME arguments 4 [sourcename: expected0]
                                    NUMBER 0.0 4 [sourcename: expected0]
                                THIS 4 [sourcename: expected0]
                        EXPR_RESULT 5 [sourcename: expected0]
                            CALL 5 [sourcename: expected0]
                                GETPROP 5 [sourcename: expected0]
                                    NAME x 5 [sourcename: expected0]
                                    STRING apply 5 [sourcename: expected0]
                                THIS 5 [sourcename: expected0]
                EXPR_RESULT 2 [sourcename: expected0]
                    CALL 2 [sourcename: expected0]
                        GETPROP 2 [sourcename: expected0]
                            NAME callback 2 [sourcename: expected0]
                            STRING apply 2 [sourcename: expected0]
                        THIS 2 [sourcename: expected0]
                        NAME arguments 2 [sourcename: expected0]


Tree2:
BLOCK [synthetic: 1]
    SCRIPT 1 [sourcename: testcode] [synthetic: 1]
        FUNCTION g 1 [sourcename: testcode]
            NAME g 1 [sourcename: testcode]
            LP 1 [sourcename: testcode]
                NAME callback 1 [sourcename: testcode]
            BLOCK 1 [sourcename: testcode]
                FUNCTION inner 4 [sourcename: testcode]
                    NAME inner 4 [sourcename: testcode]
                    LP 4 [sourcename: testcode]
                        NAME callback$$1 4 [sourcename: testcode]
                    BLOCK 4 [sourcename: testcode]
                        EXPR_RESULT 5 [sourcename: testcode]
                            ASSIGN 5 [sourcename: testcode]
                                GETELEM 5 [sourcename: testcode]
                                    NAME arguments 5 [sourcename: testcode]
                                    NUMBER 0.0 5 [sourcename: testcode]
                                THIS 5 [sourcename: testcode]
                        EXPR_RESULT 6 [sourcename: testcode]
                            CALL 6 [sourcename: testcode]
                                GETPROP 6 [sourcename: testcode]
                                    NAME callback$$1 4 [sourcename: testcode]
                                    STRING apply 6 [sourcename: testcode]
                                THIS 6 [sourcename: testcode]
                EXPR_RESULT 3 [sourcename: testcode]
                    CALL 3 [sourcename: testcode]
                        GETPROP 3 [sourcename: testcode]
                            NAME callback 2 [sourcename: testcode]
                            STRING apply 3 [sourcename: testcode]
                        THIS 3 [sourcename: testcode]
                        NAME arguments 3 [sourcename: testcode]


Subtree1: BLOCK 3 [sourcename: expected0]
    VAR 3 [sourcename: expected0]
        NAME x 3 [sourcename: expected0]
            NAME callback$$1 3 [sourcename: expected0]
    EXPR_RESULT 4 [sourcename: expected0]
        ASSIGN 4 [sourcename: expected0]
            GETELEM 4 [sourcename: expected0]
                NAME arguments 4 [sourcename: expected0]
                NUMBER 0.0 4 [sourcename: expected0]
            THIS 4 [sourcename: expected0]
    EXPR_RESULT 5 [sourcename: expected0]
        CALL 5 [sourcename: expected0]
            GETPROP 5 [sourcename: expected0]
                NAME x 5 [sourcename: expected0]
                STRING apply 5 [sourcename: expected0]
            THIS 5 [sourcename: expected0]


Subtree2: BLOCK 4 [sourcename: testcode]
    EXPR_RESULT 5 [sourcename: testcode]
        ASSIGN 5 [sourcename: testcode]
            GETELEM 5 [sourcename: testcode]
                NAME arguments 5 [sourcename: testcode]
                NUMBER 0.0 5 [sourcename: testcode]
            THIS 5 [sourcename: testcode]
    EXPR_RESULT 6 [sourcename: testcode]
        CALL 6 [sourcename: testcode]
            GETPROP 6 [sourcename: testcode]
                NAME callback$$1 4 [sourcename: testcode]
                STRING apply 6 [sourcename: testcode]
            THIS 6 [sourcename: testcode]

	at junit.framework.Assert.fail(Assert.java:57)
	at junit.framework.Assert.assertTrue(Assert.java:22)
	at junit.framework.Assert.assertNull(Assert.java:277)
	at junit.framework.TestCase.assertNull(TestCase.java:447)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:843)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:410)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:335)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:304)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:292)
	at com.google.javascript.jscomp.InlineVariablesTest.testArgumentsModifiedInInnerFunction(InlineVariablesTest.java:1035)
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
--- com.google.javascript.jscomp.InlineVariablesTest::testArgumentsModifiedInOuterFunction
junit.framework.AssertionFailedError: 
Expected: function g(callback){function inner(callback$$1){callback$$1.apply(this)}var f=callback;arguments[0]=this;f.apply(this,arguments)}
Result: function g(callback){function inner(callback$$1){callback$$1.apply(this)}arguments[0]=this;callback.apply(this,arguments)}
Node tree inequality:
Tree1:
BLOCK [synthetic: 1]
    SCRIPT 1 [sourcename: expected0] [synthetic: 1]
        FUNCTION g 1 [sourcename: expected0]
            NAME g 1 [sourcename: expected0]
            LP 1 [sourcename: expected0]
                NAME callback 1 [sourcename: expected0]
            BLOCK 1 [sourcename: expected0]
                FUNCTION inner 5 [sourcename: expected0]
                    NAME inner 5 [sourcename: expected0]
                    LP 5 [sourcename: expected0]
                        NAME callback$$1 5 [sourcename: expected0]
                    BLOCK 5 [sourcename: expected0]
                        EXPR_RESULT 5 [sourcename: expected0]
                            CALL 5 [sourcename: expected0]
                                GETPROP 5 [sourcename: expected0]
                                    NAME callback$$1 5 [sourcename: expected0]
                                    STRING apply 5 [sourcename: expected0]
                                THIS 5 [sourcename: expected0]
                VAR 2 [sourcename: expected0]
                    NAME f 2 [sourcename: expected0]
                        NAME callback 2 [sourcename: expected0]
                EXPR_RESULT 3 [sourcename: expected0]
                    ASSIGN 3 [sourcename: expected0]
                        GETELEM 3 [sourcename: expected0]
                            NAME arguments 3 [sourcename: expected0]
                            NUMBER 0.0 3 [sourcename: expected0]
                        THIS 3 [sourcename: expected0]
                EXPR_RESULT 4 [sourcename: expected0]
                    CALL 4 [sourcename: expected0]
                        GETPROP 4 [sourcename: expected0]
                            NAME f 4 [sourcename: expected0]
                            STRING apply 4 [sourcename: expected0]
                        THIS 4 [sourcename: expected0]
                        NAME arguments 4 [sourcename: expected0]


Tree2:
BLOCK [synthetic: 1]
    SCRIPT 1 [sourcename: testcode] [synthetic: 1]
        FUNCTION g 1 [sourcename: testcode]
            NAME g 1 [sourcename: testcode]
            LP 1 [sourcename: testcode]
                NAME callback 1 [sourcename: testcode]
            BLOCK 1 [sourcename: testcode]
                FUNCTION inner 5 [sourcename: testcode]
                    NAME inner 5 [sourcename: testcode]
                    LP 5 [sourcename: testcode]
                        NAME callback$$1 5 [sourcename: testcode]
                    BLOCK 5 [sourcename: testcode]
                        EXPR_RESULT 6 [sourcename: testcode]
                            CALL 6 [sourcename: testcode]
                                GETPROP 6 [sourcename: testcode]
                                    NAME callback$$1 5 [sourcename: testcode]
                                    STRING apply 6
... (truncated)
```

Your task: find the root cause and fix it in src, then verify with
`defects4j compile` and `defects4j test` that the failing test(s) pass and that
no other developer test broke.
