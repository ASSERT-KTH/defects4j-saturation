Repair a real defect in the Java project Closure (Defects4J bug Closure-174).

The working directory is a checkout of the buggy version. Layout:
  - production sources : src
  - test sources       : test   (read-only for you)

The sources currently compile. The following developer test(s) fail because of
the defect:

  - com.google.javascript.jscomp.ScopedAliasesTest::testIssue1103a
  - com.google.javascript.jscomp.ScopedAliasesTest::testIssue1103b
  - com.google.javascript.jscomp.ScopedAliasesTest::testIssue1103c

Failure output from the initial test run:

```
--- com.google.javascript.jscomp.ScopedAliasesTest::testIssue1103a
junit.framework.AssertionFailedError: Unexpected error(s): JSC_GOOG_SCOPE_NON_ALIAS_LOCAL. The local variable a is in a goog.scope and is not an alias. at testcode line 1 : 30 expected:<0> but was:<1>
	at junit.framework.Assert.fail(Assert.java:57)
	at junit.framework.Assert.failNotEquals(Assert.java:329)
	at junit.framework.Assert.assertEquals(Assert.java:78)
	at junit.framework.Assert.assertEquals(Assert.java:234)
	at junit.framework.TestCase.assertEquals(TestCase.java:401)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:871)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:477)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:403)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:372)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:360)
	at com.google.javascript.jscomp.ScopedAliasesTest.testIssue1103a(ScopedAliasesTest.java:526)
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
--- com.google.javascript.jscomp.ScopedAliasesTest::testIssue1103b
java.lang.RuntimeException: INTERNAL COMPILER ERROR.
Please report this problem.
null
  Node(FUNCTION ): testcode:1:11
goog.scope(function () {  var a = foo, b, c = 1;});
  Parent(CALL): testcode:1:0
goog.scope(function () {  var a = foo, b, c = 1;});

	at com.google.javascript.jscomp.Compiler.ensureLibraryInjected(Compiler.java:2554)
	at com.google.javascript.jscomp.ScopedAliases$Traversal.findAliases(ScopedAliases.java:373)
	at com.google.javascript.jscomp.ScopedAliases$Traversal.enterScope(ScopedAliases.java:298)
	at com.google.javascript.jscomp.NodeTraversal.pushScope(NodeTraversal.java:600)
	at com.google.javascript.jscomp.NodeTraversal.traverseFunction(NodeTraversal.java:558)
	at com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:528)
	at com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:534)
	at com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:534)
	at com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:534)
	at com.google.javascript.jscomp.NodeTraversal.traverseBranch(NodeTraversal.java:534)
	at com.google.javascript.jscomp.NodeTraversal.traverse(NodeTraversal.java:287)
	at com.google.javascript.jscomp.NodeTraversal.traverse(NodeTraversal.java:494)
	at com.google.javascript.jscomp.ScopedAliases.hotSwapScript(ScopedAliases.java:133)
	at com.google.javascript.jscomp.ScopedAliases.process(ScopedAliases.java:127)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:845)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:477)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:403)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:372)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:360)
	at com.google.javascript.jscomp.ScopedAliasesTest.testIssue1103b(ScopedAliasesTest.java:534)
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
Caused by: java.lang.NullPointerException
	... 54 more
--- com.google.javascript.jscomp.ScopedAliasesTest::testIssue1103c
junit.framework.AssertionFailedError: Unexpected error(s): JSC_GOOG_SCOPE_NON_ALIAS_LOCAL. The local variable a is in a goog.scope and is not an alias. at testcode line 1 : 52 expected:<0> but was:<1>
	at junit.framework.Assert.fail(Assert.java:57)
	at junit.framework.Assert.failNotEquals(Assert.java:329)
	at junit.framework.Assert.assertEquals(Assert.java:78)
	at junit.framework.Assert.assertEquals(Assert.java:234)
	at junit.framework.TestCase.assertEquals(TestCase.java:401)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:871)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:477)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:403)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:372)
	at com.google.javascript.jscomp.CompilerTestCase.test(CompilerTestCase.java:360)
	at com.google.javascript.jscomp.ScopedAliasesTest.testIssue1103c(ScopedAliasesTest.java:541)
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

Classes the defect is known to be located in:

  - com.google.javascript.jscomp.JsAst
  - com.google.javascript.jscomp.NodeUtil
  - com.google.javascript.jscomp.ScopedAliases

Your task: find the root cause and fix it in src, then verify with
`defects4j compile` and `defects4j test` that the failing test(s) pass and that
no other developer test broke.
