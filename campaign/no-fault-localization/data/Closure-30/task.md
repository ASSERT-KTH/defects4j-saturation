Repair a real defect in the Java project Closure (Defects4J bug Closure-30).

The working directory is a checkout of the buggy version. Layout:
  - production sources : src
  - test sources       : test   (read-only for you)

The sources currently compile. The following developer test(s) fail because of
the defect:

  - com.google.javascript.jscomp.FlowSensitiveInlineVariablesTest::testInlineAcrossSideEffect1
  - com.google.javascript.jscomp.FlowSensitiveInlineVariablesTest::testCanInlineAcrossNoSideEffect
  - com.google.javascript.jscomp.FlowSensitiveInlineVariablesTest::testIssue698

Failure output from the initial test run:

```
--- com.google.javascript.jscomp.FlowSensitiveInlineVariablesTest::testInlineAcrossSideEffect1
junit.framework.AssertionFailedError: 
Expected: function _func(){var y;var x=noSFX(y);print(x)}
Result: function _func(){var y;var x;print(noSFX(y))}
Node tree inequality:
Tree1:
BLOCK [synthetic: 1]
    SCRIPT 1 [synthetic: 1] [source_file: expected0] [input_id: InputId: expected0]
        FUNCTION _func 1 [source_file: expected0]
            NAME _func 1 [source_file: expected0]
            PARAM_LIST 1 [source_file: expected0]
            BLOCK 1 [source_file: expected0]
                VAR 1 [source_file: expected0]
                    NAME y 1 [source_file: expected0]
                VAR 1 [source_file: expected0]
                    NAME x 1 [source_file: expected0]
                        CALL 1 [free_call: 1] [source_file: expected0]
                            NAME noSFX 1 [source_file: expected0]
                            NAME y 1 [source_file: expected0]
                EXPR_RESULT 1 [source_file: expected0]
                    CALL 1 [free_call: 1] [source_file: expected0]
                        NAME print 1 [source_file: expected0]
                        NAME x 1 [source_file: expected0]


Tree2:
BLOCK [synthetic: 1]
    SCRIPT 1 [synthetic: 1] [source_file: testcode] [input_id: InputId: testcode]
        FUNCTION _func 1 [source_file: testcode]
            NAME _func 1 [source_file: testcode]
            PARAM_LIST 1 [source_file: testcode]
            BLOCK 1 [source_file: testcode]
                VAR 1 [source_file: testcode]
                    NAME y 1 [source_file: testcode]
                VAR 1 [source_file: testcode]
                    NAME x 1 [source_file: testcode]
                EXPR_RESULT 1 [source_file: testcode]
                    CALL 1 [free_call: 1] [source_file: testcode]
                        NAME print 1 [source_file: testcode]
                        CALL 1 [side_effect_flags: 15] [free_call: 1] [source_file: testcode]
                            NAME noSFX 1 [source_file: testcode]
                            NAME y 1 [source_file: testcode]


Subtree1: NAME x 1 [source_file: expected0]
    CALL 1 [free_call: 1] [source_file: expected0]
        NAME noSFX 1 [source_file: expected0]
        NAME y 1 [source_file: expected0]


Subtree2: NAME x 1 [source_file: testcode]

	at junit.framework.Assert.fail(Assert.java:57)
	at junit.framework.Assert.assertTrue(Assert.java:22)
	at junit.framework.Assert.assertNull(Assert.java:277)
	at junit.framework.TestCase.assertNull(TestCase.java:447)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:873)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:434)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:398)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:376)
	at com.google.javascript.jscomp.FlowSensitiveInlineVariablesTest.inline(FlowSensitiveInlineVariablesTest.java:443)
	at com.google.javascript.jscomp.FlowSensitiveInlineVariablesTest.noInline(FlowSensitiveInlineVariablesTest.java:439)
	at com.google.javascript.jscomp.FlowSensitiveInlineVariablesTest.testInlineAcrossSideEffect1(FlowSensitiveInlineVariablesTest.java:329)
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
--- com.google.javascript.jscomp.FlowSensitiveInlineVariablesTest::testCanInlineAcrossNoSideEffect
junit.framework.AssertionFailedError: 
Expected: function _func(){var y;var x=noSFX(y),z=noSFX();noSFX();noSFX(),print(x)}
Result: function _func(){var y;var x,z=noSFX();noSFX();noSFX(),print(noSFX(y))}
Node tree inequality:
Tree1:
BLOCK [synthetic: 1]
    SCRIPT 1 [synthetic: 1] [source_file: expected0] [input_id: InputId: expected0]
        FUNCTION _func 1 [source_file: expected0]
            NAME _func 1 [source_file: expected0]
            PARAM_LIST 1 [source_file: expected0]
            BLOCK 1 [source_file: expected0]
                VAR 1 [source_file: expected0]
                    NAME y 1 [source_file: expected0]
                VAR 1 [source_file: expected0]
                    NAME x 1 [source_file: expected0]
                        CALL 1 [free_call: 1] [source_file: expected0]
                            NAME noSFX 1 [source_file: expected0]
                            NAME y 1 [source_file: expected0]
                    NAME z 1 [source_file: expected0]
                        CALL 1 [free_call: 1] [source_file: expected0]
                            NAME noSFX 1 [source_file: expected0]
                EXPR_RESULT 1 [source_file: expected0]
                    CALL 1 [free_call: 1] [source_file: expected0]
                        NAME noSFX 1 [source_file: expected0]
                EXPR_RESULT 1 [source_file: expected0]
                    COMMA 1 [source_file: expected0]
                        CALL 1 [free_call: 1] [source_file: expected0]
                            NAME noSFX 1 [source_file: expected0]
                        CALL 1 [free_call: 1] [source_file: expected0]
                            NAME print 1 [source_file: expected0]
                            NAME x 1 [source_file: expected0]


Tree2:
BLOCK [synthetic: 1]
    SCRIPT 1 [synthetic: 1] [source_file: testcode] [input_id: InputId: testcode]
        FUNCTION _func 1 [source_file: testcode]
            NAME _func 1 [source_file: testcode]
            PARAM_LIST 1 [source_file: testcode]
            BLOCK 1 [source_file: testcode]
                VAR 1 [source_file: testcode]
                    NAME y 1 [source_file: testcode]
                VAR 1 [source_file: testcode]
                    NAME x 1 [source_file: testcode]
                    NAME z 1 [source_file: testcode]
                        CALL 1 [side_effect_flags: 15] [free_call: 1] [source_file: testcode]
                            NAME noSFX 1 [source_file: testcode]
                EXPR_RESULT 1 [source_file: testcode]
                    CALL 1 [side_effect_flags: 15] [free_call: 1] [source_file: testcode]
                        NAME noSFX 1 [source_file: testcode]
                EXPR_RESULT 1 [source_file: testcode]
                    COMMA 1 [source_file: testcode]
                        CALL 1 [side_effect_flags: 15] [free_call: 1] [source_file: testcode]
                            NAME noSFX 1 [source_file: testcode]
                        CALL 1 [free_call: 1] [source_file: testcode]
                            NAME print 1 [source_file: testcode]
                            CALL 1 [side_effect_flags: 15] [free_call: 1] [source_file: testcode]
                                NAME noSFX 1 [source_file: testcode]
                                NAME y 1 [source_file: testcode]


Subtree1: NAME x 1 [source_file: expected0]
    CALL 1 [free_call: 1] [source_file: expected0]
        NAME noSFX 1 [source_file: expected0]
        NAME y 1 [source_file: expected0]


Subtree2: NAME x 1 [source_file: testcode]

	at junit.framework.Assert.fail(Assert.java:57)
	at junit.framework.Assert.assertTrue(Assert.java:22)
	at junit.framework.Assert.assertNull(Assert.java:277)
	at junit.framework.TestCase.assertNull(TestCase.java:447)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:873)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:434)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:398)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:376)
	at com.google.javascript.jscomp.FlowSensitiveInlineVariablesTest.inline(FlowSensitiveInlineVariablesTest.java:443)
	at com.google.javascript.jscomp.FlowSensitiveInlineVariablesTest.noInline(FlowSensitiveInlineVariablesTest.java:439)
	at com.google.javascript.jscomp.FlowSensitiveInlineVariablesTest.testCanInlineAcrossNoSideEffect(FlowSensitiveInlineVariablesTest.java:363)
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
	at org.apache.tools.ant.d
... (truncated)
```

Your task: find the root cause and fix it in src, then verify with
`defects4j compile` and `defects4j test` that the failing test(s) pass and that
no other developer test broke.
