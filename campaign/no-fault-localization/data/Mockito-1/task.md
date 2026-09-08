Repair a real defect in the Java project Mockito (Defects4J bug Mockito-1).

The working directory is a checkout of the buggy version. Layout:
  - production sources : src
  - test sources       : test   (read-only for you)

The sources currently compile. The following developer test(s) fail because of
the defect:

  - org.mockito.internal.invocation.InvocationMatcherTest::should_capture_arguments_when_args_count_does_NOT_match
  - org.mockito.internal.util.reflection.FieldInitializerTest::can_instantiate_class_with_parameterized_constructor
  - org.mockito.internal.util.reflection.ParameterizedConstructorInstantiatorTest::should_report_failure_if_constructor_throws_exception
  - org.mockito.internal.util.reflection.ParameterizedConstructorInstantiatorTest::should_fail_if_an_argument_instance_type_do_not_match_wanted_type
  - org.mockito.internal.util.reflection.ParameterizedConstructorInstantiatorTest::should_instantiate_type_with_vararg_constructor
  - org.mockito.internal.util.reflection.ParameterizedConstructorInstantiatorTest::should_instantiate_type_if_resolver_provide_matching_types
  - org.mockitousage.basicapi.ResetTest::shouldRemoveAllStubbing
  - org.mockitousage.basicapi.UsingVarargsTest::shouldVerifyWithNullVarArgArray
  - org.mockitousage.basicapi.UsingVarargsTest::shouldVerifyWithAnyObject
  - org.mockitousage.basicapi.UsingVarargsTest::shouldStubBooleanVarargs
  - org.mockitousage.basicapi.UsingVarargsTest::shouldMatchEasilyEmptyVararg
  - org.mockitousage.basicapi.UsingVarargsTest::shouldVerifyBooleanVarargs
  - org.mockitousage.basicapi.UsingVarargsTest::shouldStubCorrectlyWhenMixedVarargsUsed
  - org.mockitousage.basicapi.UsingVarargsTest::shouldStubStringVarargs
  - org.mockitousage.basicapi.UsingVarargsTest::shouldStubCorrectlyWhenDoubleStringAndMixedVarargsUsed
  - org.mockitousage.basicapi.UsingVarargsTest::shouldVerifyStringVarargs
  - org.mockitousage.basicapi.UsingVarargsTest::shouldVerifyObjectVarargs
  - org.mockitousage.bugs.VarargsErrorWhenCallingRealMethodTest::shouldNotThrowAnyException
  - org.mockitousage.bugs.varargs.VarargsAndAnyObjectPicksUpExtraInvocationsTest::shouldVerifyCorrectlyWithAnyVarargs
  - org.mockitousage.bugs.varargs.VarargsAndAnyObjectPicksUpExtraInvocationsTest::shouldVerifyCorrectlyNumberOfInvocationsUsingAnyVarargAndEqualArgument
  - org.mockitousage.bugs.varargs.VarargsNotPlayingWithAnyObjectTest::shouldStubUsingAnyVarargs
  - org.mockitousage.matchers.VerificationAndStubbingUsingMatchersTest::shouldVerifyUsingMatchers
  - org.mockitousage.stubbing.BasicStubbingTest::test_stub_only_not_verifiable
  - org.mockitousage.stubbing.BasicStubbingTest::should_evaluate_latest_stubbing_first
  - org.mockitousage.stubbing.DeprecatedStubbingTest::shouldEvaluateLatestStubbingFirst
  - org.mockitousage.verification.VerificationInOrderMixedWithOrdiraryVerificationTest::shouldUseEqualsToVerifyMethodVarargs

Failure output from the initial test run:

```
--- org.mockito.internal.invocation.InvocationMatcherTest::should_capture_arguments_when_args_count_does_NOT_match
java.lang.UnsupportedOperationException
	at org.mockito.internal.invocation.InvocationMatcher.captureArgumentsFrom(InvocationMatcher.java:123)
	at org.mockito.internal.invocation.InvocationMatcherTest.should_capture_arguments_when_args_count_does_NOT_match(InvocationMatcherTest.java:170)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:62)
	at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
	at java.base/java.lang.reflect.Method.invoke(Method.java:566)
	at org.junit.runners.model.FrameworkMethod$1.runReflectiveCall(FrameworkMethod.java:50)
	at org.junit.internal.runners.model.ReflectiveCallable.run(ReflectiveCallable.java:12)
	at org.junit.runners.model.FrameworkMethod.invokeExplosively(FrameworkMethod.java:47)
	at org.junit.internal.runners.statements.InvokeMethod.evaluate(InvokeMethod.java:17)
	at org.junit.internal.runners.statements.RunBefores.evaluate(RunBefores.java:26)
	at org.junit.internal.runners.statements.RunAfters.evaluate(RunAfters.java:27)
	at org.junit.runners.ParentRunner.runLeaf(ParentRunner.java:325)
	at org.junit.runners.BlockJUnit4ClassRunner.runChild(BlockJUnit4ClassRunner.java:78)
	at org.junit.runners.BlockJUnit4ClassRunner.runChild(BlockJUnit4ClassRunner.java:57)
	at org.junit.runners.ParentRunner$3.run(ParentRunner.java:290)
	at org.junit.runners.ParentRunner$1.schedule(ParentRunner.java:71)
	at org.junit.runners.ParentRunner.runChildren(ParentRunner.java:288)
	at org.junit.runners.ParentRunner.access$000(ParentRunner.java:58)
	at org.junit.runners.ParentRunner$2.evaluate(ParentRunner.java:268)
	at org.junit.runners.ParentRunner.run(ParentRunner.java:363)
	at junit.framework.JUnit4TestAdapter.run(JUnit4TestAdapter.java:38)
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
--- org.mockito.internal.util.reflection.FieldInitializerTest::can_instantiate_class_with_parameterized_constructor
java.lang.UnsupportedOperationException
	at org.mockito.internal.invocation.InvocationMatcher.captureArgumentsFrom(InvocationMatcher.java:123)
	at org.mockito.internal.handler.MockHandlerImpl.handle(MockHandlerImpl.java:94)
	at org.mockito.internal.handler.NullResultGuardian.handle(NullResultGuardian.java:29)
	at org.mockito.internal.handler.InvocationNotifierHandler.handle(InvocationNotifierHandler.java:37)
	at org.mockito.internal.creation.bytebuddy.MockMethodInterceptor.doIntercept(MockMethodInterceptor.java:82)
	at org.mockito.internal.creation.bytebuddy.MockMethodInterceptor.interceptAbstract(MockMethodInterceptor.java:70)
	at org.mockito.internal.util.reflection.FieldInitializer$ConstructorArgumentResolver$MockitoMock$705721624.resolveTypeInstances(Unknown Source)
	at org.mockito.internal.util.reflection.FieldInitializer$ParameterizedConstructorInstantiator.instantiate(FieldInitializer.java:256)
	at org.mockito.internal.util.reflection.FieldInitializer.acquireFieldInstance(FieldInitializer.java:124)
	at org.mockito.internal.util.reflection.FieldInitializer.initialize(FieldInitializer.java:86)
	at org.mockito.internal.util.reflection.FieldInitializerTest.can_instantiate_class_with_parameterized_constructor(FieldInitializerTest.java:162)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:62)
	at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
	at java.base/java.lang.reflect.Method.invoke(Method.java:566)
	at org.junit.runners.model.FrameworkMethod$1.runReflectiveCall(FrameworkMethod.java:50)
	at org.junit.internal.runners.model.ReflectiveCallable.run(ReflectiveCallable.java:12)
	at org.junit.runners.model.FrameworkMethod.invokeExplosively(FrameworkMethod.java:47)
	at org.junit.internal.runners.statements.InvokeMethod.evaluate(InvokeMethod.java:17)
	at org.junit.runners.ParentRunner.runLeaf(ParentRunner.java:325)
	at org.junit.runners.BlockJUnit4ClassRunner.runChild(BlockJUnit4ClassRunner.java:78)
	at org.junit.runners.BlockJUnit4ClassRunner.runChild(BlockJUnit4ClassRunner.java:57)
	at org.junit.runners.ParentRunner$3.run(ParentRunner.java:290)
	at org.junit.runners.ParentRunner$1.schedule(ParentRunner.java:71)
	at org.junit.runners.ParentRunner.runChildren(ParentRunner.java:288)
	at org.junit.runners.ParentRunner.access$000(ParentRunner.java:58)
	at org.junit.runners.ParentRunner$2.evaluate(ParentRunner.java:268)
	at org.junit.runners.ParentRunner.run(ParentRunner.java:363)
	at junit.framework.JUnit4TestAdapter.run(JUnit4TestAdapter.java:38)
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
--- org.mockito.internal.util.reflection.ParameterizedConstructorInstantiatorTest::should_report_failure_if_constructor_throws_exception
java.lang.UnsupportedOperationException
	at org.mockito.internal.invocation.InvocationMatcher.captureArgumentsFrom(InvocationMatcher.java:123)
	at org.mockito.internal.handler.MockHandlerImpl.handle(MockHandlerImpl.java:94)
	at org.mockito.internal.handler.NullResultGuardian.handle(NullResultGuardian.java:29)
	at org.mockito.internal.handler.InvocationNotifierHandler.handle(InvocationNotifierHandler.java:37)
	at org.mockito.internal.creation.bytebuddy.MockMethodInterceptor.doIntercept(MockMethodInterceptor.java:82)
	at org.mockito.internal.creation.bytebuddy.MockMethodInterceptor.interceptAbstract(MockMethodInterceptor.java:70)
	at org.mockito.internal.util.reflection.FieldInitializer$ConstructorArgumentResolver$MockitoMock$1857659842.resolveTypeInstances(Unknown Source)
	at org.mockito.internal.util.reflection.FieldInitializer$ParameterizedConstructorInstantiator.instantiate(FieldInitializer.java:256)
	at org.mockito.internal.util.reflection.ParameterizedConstructorInstantiatorTest.should_report_failure_if_constructor_throws_exception(ParameterizedConstructorInstantiatorTest.java:101)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:62)
	at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
	at java.base/java.lang.reflect.Method.invoke(Method.java:566)
	at org.junit.runners.model.FrameworkMethod$1.runReflectiveCall(FrameworkMethod.java:50)
	at org.junit.internal.runners.model.ReflectiveCallable.run(ReflectiveCallable.java:12)
	at org.junit.runners.model.FrameworkMethod.invokeExplosively(FrameworkMethod.java:47)
	at org.junit.internal.runners.statements.InvokeMethod.evaluate(InvokeMethod.java:17)
	at org.junit.internal.runners.statements.RunAfters.evaluate(RunAfters.java:27)
	at org.junit.runners.ParentRunner.runLeaf(ParentRunner.java:325)
	at org.junit.runners.BlockJUnit4ClassRunner.runChild(BlockJUnit4ClassRunner.java:78)
	at org.junit.runners.BlockJUnit4ClassRunner.runChild(BlockJUnit4ClassRunner.java:57)
	at org.junit.runners.ParentRunner$3.run(ParentRunner.java:290)
	at org.junit.runners.ParentRunner$1.schedule(ParentRunner.java:71)
	at org.junit.runners.ParentRunner.runChildren(ParentRunner.java:288)
	at org.junit.runners.ParentRunner.access$000(ParentRunner.java:58)
	at org.junit.runners.ParentRunner$2.evaluate(ParentRunner.java:268)
	at org.junit.runners.ParentRunner.run(ParentRunner.java:363)
	at org.mockito.internal.runners.JUnit45AndHigherRunnerImpl.run(JUnit45AndHigherRunnerImpl.java:37)
	at org.mockito.runners.MockitoJUnitRunner.run(MockitoJUnitRunner.java:62)
	at junit.framework.JUnit4TestAdapter.run(JUnit4TestAdapter.java:38)
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
	at 
... (truncated)
```

Your task: find the root cause and fix it in src, then verify with
`defects4j compile` and `defects4j test` that the failing test(s) pass and that
no other developer test broke.
