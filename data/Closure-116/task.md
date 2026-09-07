Repair a real defect in the Java project Closure (Defects4J bug Closure-116).

The working directory is a checkout of the buggy version. Layout:
  - production sources : src
  - test sources       : test   (read-only for you)

The sources currently compile. The following developer test(s) fail because of
the defect:

  - com.google.javascript.jscomp.FunctionInjectorTest::testIssue1101a
  - com.google.javascript.jscomp.FunctionInjectorTest::testIssue1101b
  - com.google.javascript.jscomp.InlineFunctionsTest::testBug4944818
  - com.google.javascript.jscomp.InlineFunctionsTest::testDoubleInlining2
  - com.google.javascript.jscomp.InlineFunctionsTest::testIssue1101
  - com.google.javascript.jscomp.InlineFunctionsTest::testInlineIfParametersModified8
  - com.google.javascript.jscomp.InlineFunctionsTest::testInlineIfParametersModified9
  - com.google.javascript.jscomp.InlineFunctionsTest::testInlineFunctions6

Failure output from the initial test run:

```
--- com.google.javascript.jscomp.FunctionInjectorTest::testIssue1101a
junit.framework.AssertionFailedError: expected:<NO> but was:<YES>
	at junit.framework.Assert.fail(Assert.java:57)
	at junit.framework.Assert.failNotEquals(Assert.java:329)
	at junit.framework.Assert.assertEquals(Assert.java:78)
	at junit.framework.Assert.assertEquals(Assert.java:86)
	at com.google.javascript.jscomp.FunctionInjectorTest$1.call(FunctionInjectorTest.java:1404)
	at com.google.javascript.jscomp.FunctionInjectorTest$TestCallback.visit(FunctionInjectorTest.java:1545)
	at com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:540)
	at com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:534)
	at com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:534)
	at com.google.javascript.jscomp.NodeTraversal.traverse(NodeTraversal.java:287)
	at com.google.javascript.jscomp.NodeTraversal.traverse(NodeTraversal.java:494)
	at com.google.javascript.jscomp.FunctionInjectorTest.helperCanInlineReferenceToFunction(FunctionInjectorTest.java:1411)
	at com.google.javascript.jscomp.FunctionInjectorTest.helperCanInlineReferenceToFunction(FunctionInjectorTest.java:1375)
	at com.google.javascript.jscomp.FunctionInjectorTest.testIssue1101a(FunctionInjectorTest.java:1347)
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
--- com.google.javascript.jscomp.FunctionInjectorTest::testIssue1101b
junit.framework.AssertionFailedError: expected:<NO> but was:<YES>
	at junit.framework.Assert.fail(Assert.java:57)
	at junit.framework.Assert.failNotEquals(Assert.java:329)
	at junit.framework.Assert.assertEquals(Assert.java:78)
	at junit.framework.Assert.assertEquals(Assert.java:86)
	at com.google.javascript.jscomp.FunctionInjectorTest$1.call(FunctionInjectorTest.java:1404)
	at com.google.javascript.jscomp.FunctionInjectorTest$TestCallback.visit(FunctionInjectorTest.java:1545)
	at com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:540)
	at com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:534)
	at com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:534)
	at com.google.javascript.jscomp.NodeTraversal.traverse(NodeTraversal.java:287)
	at com.google.javascript.jscomp.NodeTraversal.traverse(NodeTraversal.java:494)
	at com.google.javascript.jscomp.FunctionInjectorTest.helperCanInlineReferenceToFunction(FunctionInjectorTest.java:1411)
	at com.google.javascript.jscomp.FunctionInjectorTest.helperCanInlineReferenceToFunction(FunctionInjectorTest.java:1375)
	at com.google.javascript.jscomp.FunctionInjectorTest.testIssue1101b(FunctionInjectorTest.java:1353)
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
--- com.google.javascript.jscomp.InlineFunctionsTest::testBug4944818
junit.framework.AssertionFailedError: 
Expected: HangoutStarter.prototype.launchHangout=function(){var self$$2=a.b;var JSCompiler_temp_const$$0=goog.Uri;var JSCompiler_inline_result$$1;var JSCompiler_inline_result$$0;var self$$inline_1=self$$2;if(!self$$inline_1.domServices_)self$$inline_1.domServices_=goog$component$DomServices.get(self$$inline_1.appContext_);JSCompiler_inline_result$$0=self$$inline_1.domServices_;JSCompiler_inline_result$$1=JSCompiler_inline_result$$0.getDomHelper().getWindow();var myUrl=new JSCompiler_temp_const$$0(JSCompiler_inline_result$$1.location.href)}
Result: HangoutStarter.prototype.launchHangout=function(){var self$$2=a.b;var JSCompiler_temp_const$$0=goog.Uri;var JSCompiler_inline_result$$1;var self$$inline_2=self$$2;if(!self$$inline_2.domServices_)self$$inline_2.domServices_=goog$component$DomServices.get(self$$inline_2.appContext_);JSCompiler_inline_result$$1=self$$inline_2.domServices_;var myUrl=new JSCompiler_temp_const$$0(JSCompiler_inline_result$$1.getDomHelper().getWindow().location.href)}
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
                                NAME JSCompiler_inline_result$$0 1 [source_file: expected0]
                            BLOCK 1 [source_file: expected0]
                                VAR 1 [source_file: expected0]
                                    NAME self$$inline_1 1 [source_file: expected0]
                                        NAME self$$2 1 [source_file: expected0]
                                IF 1 [source_file: expected0]
                                    NOT 1 [source_file: expected0]
                                        GETPROP 1 [source_file: expected0]
                                            NAME self$$inline_1 1 [source_file: expected0]
                                            STRING domServices_ 1 [source_file: expected0]
                                    BLOCK 1 [source_file: expected0]
                                        EXPR_RESULT 1 [source_file: expected0]
                                            ASSIGN 1 [source_file: expected0]
                                                GETPROP 1 [source_file: expected0]
                                                    NAME self$$inline_1 1 [source_file: expected0]
                                                    STRING domServices_ 1 [source_file: expected0]
                                                CALL 1 [source_file: expected0]
                                                    GETPROP 1 [source_file: expected0]
                                                        NAME goog$component$DomServices 1 [source_file: expected0]
                                                        STRING get 1
... (truncated)
```

Classes the defect is known to be located in:

  - com.google.javascript.jscomp.FunctionInjector

Your task: find the root cause and fix it in src, then verify with
`defects4j compile` and `defects4j test` that the failing test(s) pass and that
no other developer test broke.
