Repair a real defect in the Java project Closure (Defects4J bug Closure-125).

The working directory is a checkout of the buggy version. Layout:
  - production sources : src
  - test sources       : test   (read-only for you)

The sources currently compile. The following developer test(s) fail because of
the defect:

  - com.google.javascript.jscomp.TypeCheckTest::testIssue1002

Failure output from the initial test run:

```
--- com.google.javascript.jscomp.TypeCheckTest::testIssue1002
java.lang.IllegalStateException
	at com.google.common.base.Preconditions.checkState(Preconditions.java:133)
	at com.google.javascript.rhino.jstype.FunctionType.getInstanceType(FunctionType.java:1071)
	at com.google.javascript.jscomp.TypeCheck.visitNew(TypeCheck.java:1663)
	at com.google.javascript.jscomp.TypeCheck.visit(TypeCheck.java:591)
	at com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:540)
	at com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:534)
	at com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:534)
	at com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:534)
	at com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:534)
	at com.google.javascript.jscomp.NodeTraversal.traverseFunction(NodeTraversal.java:574)
	at com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:528)
	at com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:534)
	at com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:534)
	at com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:534)
	at com.google.javascript.jscomp.NodeTraversal.traverseWithScope(NodeTraversal.java:353)
	at com.google.javascript.jscomp.TypeCheck.check(TypeCheck.java:422)
	at com.google.javascript.jscomp.TypeCheck.process(TypeCheck.java:393)
	at com.google.javascript.jscomp.TypeCheck.processForTesting(TypeCheck.java:411)
	at com.google.javascript.jscomp.TypeCheckTest.parseAndTypeCheckWithScope(TypeCheckTest.java:12021)
	at com.google.javascript.jscomp.TypeCheckTest.parseAndTypeCheck(TypeCheckTest.java:11993)
	at com.google.javascript.jscomp.TypeCheckTest.testTypes(TypeCheckTest.java:11960)
	at com.google.javascript.jscomp.TypeCheckTest.testTypes(TypeCheckTest.java:11955)
	at com.google.javascript.jscomp.TypeCheckTest.testTypes(TypeCheckTest.java:11891)
	at com.google.javascript.jscomp.TypeCheckTest.testTypes(TypeCheckTest.java:11887)
	at com.google.javascript.jscomp.TypeCheckTest.testIssue1002(TypeCheckTest.java:6741)
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
```

Your task: find the root cause and fix it in src, then verify with
`defects4j compile` and `defects4j test` that the failing test(s) pass and that
no other developer test broke.
