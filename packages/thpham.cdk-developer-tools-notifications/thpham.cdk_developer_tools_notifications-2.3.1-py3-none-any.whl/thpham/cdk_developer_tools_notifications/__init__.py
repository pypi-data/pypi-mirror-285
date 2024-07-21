'''
[![cdk-constructs Logo](https://raw.githubusercontent.com/thpham/cdk-constructs/master/logo.png)](https://github.com/thpham/cdk-constructs)

# @ithings/cdk-developer-tools-notifications

[![Build Status](https://github.com/thpham/cdk-constructs/workflows/Build/badge.svg)](https://github.com/thpham/cdk-constructs/actions?query=workflow=Build)
[![cdkdx](https://img.shields.io/badge/buildtool-cdkdx-blue.svg)](https://github.com/hupe1980/cdkdx)
[![typescript](https://img.shields.io/badge/jsii-typescript-blueviolet.svg)](https://www.npmjs.com/package/@ithings/cdk-developer-tools-notifications)
[![python](https://img.shields.io/badge/jsii-python-blueviolet.svg)](https://pypi.org/project/thpham.cdk-developer-tools-notifications/)
[![Mentioned in Awesome CDK](https://awesome.re/mentioned-badge.svg)](https://github.com/kolomied/awesome-cdk)

> #slack / msteams / email notifications for developer tools: CodeCommit, CodeBuild, CodeDeploy, CodePipeline

## Install

TypeScript/JavaScript:

```bash
npm i @ithings/cdk-developer-tools-notifications
```

Python:

```bash
pip install thpham.cdk-developer-tools-notifications
```

## MSTeams

[Add incoming webhook](https://docs.microsoft.com/de-de/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook):

1. Navigate to the channel where you want to add the webhook and select (•••) More Options from the top navigation bar.
2. Choose Connectors from the drop-down menu and search for Incoming Webhook.
3. Select the Configure button, provide a name, and, optionally, upload an image avatar for your webhook.
4. The dialog window will present a unique URL that will map to the channel. Make sure that you copy and save the URL—you will need to provide it to the outside service.
5. Select the Done button. The webhook will be available in the team channel.

![codepipeline message](https://raw.githubusercontent.com/thpham/cdk-constructs/master/packages/cdk-developer-tools-notifications/assets/codepipeline-message.png)

## #Slack

[Notifications for AWS developer tools](https://docs.aws.amazon.com/chatbot/latest/adminguide/related-services.html#codeserviceevents)

## How to use

```python
import { SlackChannelConfiguration, MSTeamsIncomingWebhookConfiguration, AccountLabelMode } from '@ithings/cdk-chatops';
import {
  RepositoryNotificationRule,
  PipelineNotificationRule,
  RepositoryEvent,
  PipelineEvent,
  SlackChannel,
  MSTeamsIncomingWebhook,
} from '@ithings/cdk-developer-tools-notifications';
import { Stack, StackProps } from 'aws-cdk-lib';
import { Repository } from 'aws-cdk-lib/aws-codecommit';
import { Pipeline, Artifact } from 'aws-cdk-lib/aws-codepipeline';
import { CodeCommitSourceAction, ManualApprovalAction } from 'aws-cdk-lib/aws-codepipeline-actions';
import { Construct } from 'constructs';

export class NotificationsStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const repository = new Repository(this, 'Repository', {
      repositoryName: 'notifications-repository',
    });

    if (typeof process.env.SLACK_WORKSPACE_ID === 'undefined') {
      throw new Error('environment variable SLACK_WORKSPACE_ID undefined');
    }
    if (typeof process.env.SLACK_CHANNEL_ID === 'undefined') {
      throw new Error('environment variable SLACK_CHANNEL_ID undefined');
    }
    const slackChannel = new SlackChannelConfiguration(this, 'SlackChannel', {
      slackWorkspaceId: process.env.SLACK_WORKSPACE_ID,
      configurationName: 'notifications',
      slackChannelId: process.env.SLACK_CHANNEL_ID,
    });

    if (typeof process.env.INCOMING_WEBHOOK_URL === 'undefined') {
      throw new Error('environment variable INCOMING_WEBHOOK_URL undefined');
    }
    const webhook = new MSTeamsIncomingWebhookConfiguration(this, 'MSTeamsWebhook', {
      url: process.env.INCOMING_WEBHOOK_URL,
      accountLabelMode: AccountLabelMode.ID_AND_ALIAS,
      themeColor: '#FF0000',
    });

    new RepositoryNotificationRule(this, 'RepoNotifications', {
      name: 'notifications-repository',
      repository,
      events: [RepositoryEvent.COMMENTS_ON_COMMITS, RepositoryEvent.PULL_REQUEST_CREATED, RepositoryEvent.PULL_REQUEST_MERGED],
      targets: [new SlackChannel(slackChannel), new MSTeamsIncomingWebhook(webhook)],
    });

    const sourceArtifact = new Artifact();

    const sourceAction = new CodeCommitSourceAction({
      actionName: 'CodeCommit',
      repository,
      output: sourceArtifact,
    });

    const approvalAction = new ManualApprovalAction({
      actionName: 'Approval',
    });

    const pipeline = new Pipeline(this, 'Pipeline', {
      pipelineName: 'notifications-pipeline',
      stages: [
        {
          stageName: 'Source',
          actions: [sourceAction],
        },
        {
          stageName: 'Approval',
          actions: [approvalAction],
        },
      ],
    });

    new PipelineNotificationRule(this, 'PipelineNotificationRule', {
      name: 'pipeline-notification',
      pipeline,
      events: [
        PipelineEvent.PIPELINE_EXECUTION_STARTED,
        PipelineEvent.PIPELINE_EXECUTION_FAILED,
        PipelineEvent.PIPELINE_EXECUTION_SUCCEEDED,
        // PipelineEvent.ACTION_EXECUTION_STARTED,
        // PipelineEvent.ACTION_EXECUTION_SUCCEEDED,
        // PipelineEvent.ACTION_EXECUTION_FAILED,
        PipelineEvent.MANUAL_APPROVAL_NEEDED,
        PipelineEvent.MANUAL_APPROVAL_SUCCEEDED,
        // PipelineEvent.MANUAL_APPROVAL_FAILED,
        // PipelineEvent.STAGE_EXECUTION_STARTED,
        // PipelineEvent.STAGE_EXECUTION_SUCCEEDED,
        // PipelineEvent.STAGE_EXECUTION_FAILED,
      ],
      targets: [new SlackChannel(slackChannel), new MSTeamsIncomingWebhook(webhook)],
    });
  }
}
```

## API Reference

See [API.md](https://github.com/thpham/cdk-constructs/tree/master/packages/cdk-developer-tools-notifications/API.md).

## Example

See more complete [examples](https://github.com/thpham/cdk-constructs/tree/master/examples).

## License

[MIT](https://github.com/thpham/cdk-constructs/tree/master/packages/cdk-developer-tools-notifications/LICENSE)
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from typeguard import check_type

from ._jsii import *

import aws_cdk.aws_codebuild as _aws_cdk_aws_codebuild_ceddda9d
import aws_cdk.aws_codecommit as _aws_cdk_aws_codecommit_ceddda9d
import aws_cdk.aws_codedeploy as _aws_cdk_aws_codedeploy_ceddda9d
import aws_cdk.aws_codepipeline as _aws_cdk_aws_codepipeline_ceddda9d
import aws_cdk.aws_sns as _aws_cdk_aws_sns_ceddda9d
import constructs as _constructs_77d1e7e8
import thpham.cdk_chatops as _thpham_cdk_chatops_e462e3bd


@jsii.enum(jsii_type="@ithings/cdk-developer-tools-notifications.ApplicationEvent")
class ApplicationEvent(enum.Enum):
    DEPLOYMENT_FAILED = "DEPLOYMENT_FAILED"
    DEPLOYMENT_SUCCEEDED = "DEPLOYMENT_SUCCEEDED"
    DEPLOYMENT_STARTED = "DEPLOYMENT_STARTED"


@jsii.data_type(
    jsii_type="@ithings/cdk-developer-tools-notifications.CommonNotificationRuleProps",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "detail_type": "detailType",
        "status": "status",
        "targets": "targets",
    },
)
class CommonNotificationRuleProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        detail_type: typing.Optional["DetailType"] = None,
        status: typing.Optional["Status"] = None,
        targets: typing.Optional[typing.Sequence["INotificationTarget"]] = None,
    ) -> None:
        '''
        :param name: The name for the notification rule. Notification rule names must be unique in your AWS account.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: FULL
        :param status: The status of the notification rule. The default value is ENABLED. If the status is set to DISABLED, notifications aren't sent for the notification rule. Default: ENABLED
        :param targets: SNS topics or AWS Chatbot clients to associate with the notification rule.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a937243bd2bef97f731586167f55110a65585b66de15fefb6b51e3fea67e6fc)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument detail_type", value=detail_type, expected_type=type_hints["detail_type"])
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
            check_type(argname="argument targets", value=targets, expected_type=type_hints["targets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if detail_type is not None:
            self._values["detail_type"] = detail_type
        if status is not None:
            self._values["status"] = status
        if targets is not None:
            self._values["targets"] = targets

    @builtins.property
    def name(self) -> builtins.str:
        '''The name for the notification rule.

        Notification rule names
        must be unique in your AWS account.
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def detail_type(self) -> typing.Optional["DetailType"]:
        '''The level of detail to include in the notifications for this resource.

        BASIC will include only the contents of the event
        as it would appear in AWS CloudWatch. FULL will include any
        supplemental information provided by AWS CodeStar Notifications
        and/or the service for the resource for which the notification
        is created.

        :default: FULL
        '''
        result = self._values.get("detail_type")
        return typing.cast(typing.Optional["DetailType"], result)

    @builtins.property
    def status(self) -> typing.Optional["Status"]:
        '''The status of the notification rule.

        The default value is ENABLED.
        If the status is set to DISABLED, notifications aren't sent for
        the notification rule.

        :default: ENABLED
        '''
        result = self._values.get("status")
        return typing.cast(typing.Optional["Status"], result)

    @builtins.property
    def targets(self) -> typing.Optional[typing.List["INotificationTarget"]]:
        '''SNS topics or AWS Chatbot clients to associate with the notification rule.'''
        result = self._values.get("targets")
        return typing.cast(typing.Optional[typing.List["INotificationTarget"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CommonNotificationRuleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@ithings/cdk-developer-tools-notifications.DetailType")
class DetailType(enum.Enum):
    FULL = "FULL"
    BASIC = "BASIC"


@jsii.interface(
    jsii_type="@ithings/cdk-developer-tools-notifications.INotificationRule"
)
class INotificationRule(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="notificationRuleArn")
    def notification_rule_arn(self) -> builtins.str:
        ...


class _INotificationRuleProxy:
    __jsii_type__: typing.ClassVar[str] = "@ithings/cdk-developer-tools-notifications.INotificationRule"

    @builtins.property
    @jsii.member(jsii_name="notificationRuleArn")
    def notification_rule_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notificationRuleArn"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, INotificationRule).__jsii_proxy_class__ = lambda : _INotificationRuleProxy


@jsii.interface(
    jsii_type="@ithings/cdk-developer-tools-notifications.INotificationTarget"
)
class INotificationTarget(typing_extensions.Protocol):
    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _constructs_77d1e7e8.Construct,
        rule: INotificationRule,
    ) -> "NotificationTargetProperty":
        '''
        :param scope: -
        :param rule: -
        '''
        ...


class _INotificationTargetProxy:
    __jsii_type__: typing.ClassVar[str] = "@ithings/cdk-developer-tools-notifications.INotificationTarget"

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _constructs_77d1e7e8.Construct,
        rule: INotificationRule,
    ) -> "NotificationTargetProperty":
        '''
        :param scope: -
        :param rule: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b541b2224cd7d8ca242f888c6ceab1812dfe9ca62b16fffb866f5ed2e8011e98)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument rule", value=rule, expected_type=type_hints["rule"])
        return typing.cast("NotificationTargetProperty", jsii.invoke(self, "bind", [scope, rule]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, INotificationTarget).__jsii_proxy_class__ = lambda : _INotificationTargetProxy


@jsii.implements(INotificationTarget)
class MSTeamsIncomingWebhook(
    metaclass=jsii.JSIIMeta,
    jsii_type="@ithings/cdk-developer-tools-notifications.MSTeamsIncomingWebhook",
):
    def __init__(
        self,
        webhook: _thpham_cdk_chatops_e462e3bd.MSTeamsIncomingWebhookConfiguration,
    ) -> None:
        '''
        :param webhook: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__730bc001b37af829435fb7e9c7d533d5e64c2a9c689f8caac23c118946ff9260)
            check_type(argname="argument webhook", value=webhook, expected_type=type_hints["webhook"])
        jsii.create(self.__class__, self, [webhook])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _constructs_77d1e7e8.Construct,
        _rule: INotificationRule,
    ) -> "NotificationTargetProperty":
        '''
        :param scope: -
        :param _rule: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b831de9b8b1c3e926d3d65bf9b15eeca85dfd72ce9a5e92be24d3780bbb21d0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument _rule", value=_rule, expected_type=type_hints["_rule"])
        return typing.cast("NotificationTargetProperty", jsii.invoke(self, "bind", [scope, _rule]))


@jsii.implements(INotificationRule)
class NotificationRule(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@ithings/cdk-developer-tools-notifications.NotificationRule",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        events: typing.Sequence[typing.Union["RepositoryEvent", "PipelineEvent", "ProjectEvent", ApplicationEvent]],
        resource: builtins.str,
        name: builtins.str,
        detail_type: typing.Optional[DetailType] = None,
        status: typing.Optional["Status"] = None,
        targets: typing.Optional[typing.Sequence[INotificationTarget]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param events: A list of events associated with this notification rule.
        :param resource: The Amazon Resource Name (ARN) of the resource to associate with the notification rule. Supported resources include pipelines in AWS CodePipeline, repositories in AWS CodeCommit, and build projects in AWS CodeBuild.
        :param name: The name for the notification rule. Notification rule names must be unique in your AWS account.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: FULL
        :param status: The status of the notification rule. The default value is ENABLED. If the status is set to DISABLED, notifications aren't sent for the notification rule. Default: ENABLED
        :param targets: SNS topics or AWS Chatbot clients to associate with the notification rule.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be764047800f4e67e91c73cea28b16a9d91598104b2e4f5bd4b840c4f0b9a1d5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = NotificationRuleProps(
            events=events,
            resource=resource,
            name=name,
            detail_type=detail_type,
            status=status,
            targets=targets,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addTarget")
    def add_target(self, target: INotificationTarget) -> None:
        '''
        :param target: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67e7aaaf439297abc0f5d41fccb066e3a3979d67370d947d244889cfccd44876)
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        return typing.cast(None, jsii.invoke(self, "addTarget", [target]))

    @builtins.property
    @jsii.member(jsii_name="notificationRuleArn")
    def notification_rule_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notificationRuleArn"))


@jsii.data_type(
    jsii_type="@ithings/cdk-developer-tools-notifications.NotificationRuleProps",
    jsii_struct_bases=[CommonNotificationRuleProps],
    name_mapping={
        "name": "name",
        "detail_type": "detailType",
        "status": "status",
        "targets": "targets",
        "events": "events",
        "resource": "resource",
    },
)
class NotificationRuleProps(CommonNotificationRuleProps):
    def __init__(
        self,
        *,
        name: builtins.str,
        detail_type: typing.Optional[DetailType] = None,
        status: typing.Optional["Status"] = None,
        targets: typing.Optional[typing.Sequence[INotificationTarget]] = None,
        events: typing.Sequence[typing.Union["RepositoryEvent", "PipelineEvent", "ProjectEvent", ApplicationEvent]],
        resource: builtins.str,
    ) -> None:
        '''
        :param name: The name for the notification rule. Notification rule names must be unique in your AWS account.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: FULL
        :param status: The status of the notification rule. The default value is ENABLED. If the status is set to DISABLED, notifications aren't sent for the notification rule. Default: ENABLED
        :param targets: SNS topics or AWS Chatbot clients to associate with the notification rule.
        :param events: A list of events associated with this notification rule.
        :param resource: The Amazon Resource Name (ARN) of the resource to associate with the notification rule. Supported resources include pipelines in AWS CodePipeline, repositories in AWS CodeCommit, and build projects in AWS CodeBuild.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88462a85c912a642d612e9157fe1f4ad046391d9eaff76429454bca05a8c6fe8)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument detail_type", value=detail_type, expected_type=type_hints["detail_type"])
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
            check_type(argname="argument targets", value=targets, expected_type=type_hints["targets"])
            check_type(argname="argument events", value=events, expected_type=type_hints["events"])
            check_type(argname="argument resource", value=resource, expected_type=type_hints["resource"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "events": events,
            "resource": resource,
        }
        if detail_type is not None:
            self._values["detail_type"] = detail_type
        if status is not None:
            self._values["status"] = status
        if targets is not None:
            self._values["targets"] = targets

    @builtins.property
    def name(self) -> builtins.str:
        '''The name for the notification rule.

        Notification rule names
        must be unique in your AWS account.
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def detail_type(self) -> typing.Optional[DetailType]:
        '''The level of detail to include in the notifications for this resource.

        BASIC will include only the contents of the event
        as it would appear in AWS CloudWatch. FULL will include any
        supplemental information provided by AWS CodeStar Notifications
        and/or the service for the resource for which the notification
        is created.

        :default: FULL
        '''
        result = self._values.get("detail_type")
        return typing.cast(typing.Optional[DetailType], result)

    @builtins.property
    def status(self) -> typing.Optional["Status"]:
        '''The status of the notification rule.

        The default value is ENABLED.
        If the status is set to DISABLED, notifications aren't sent for
        the notification rule.

        :default: ENABLED
        '''
        result = self._values.get("status")
        return typing.cast(typing.Optional["Status"], result)

    @builtins.property
    def targets(self) -> typing.Optional[typing.List[INotificationTarget]]:
        '''SNS topics or AWS Chatbot clients to associate with the notification rule.'''
        result = self._values.get("targets")
        return typing.cast(typing.Optional[typing.List[INotificationTarget]], result)

    @builtins.property
    def events(
        self,
    ) -> typing.List[typing.Union["RepositoryEvent", "PipelineEvent", "ProjectEvent", ApplicationEvent]]:
        '''A list of events associated with this notification rule.'''
        result = self._values.get("events")
        assert result is not None, "Required property 'events' is missing"
        return typing.cast(typing.List[typing.Union["RepositoryEvent", "PipelineEvent", "ProjectEvent", ApplicationEvent]], result)

    @builtins.property
    def resource(self) -> builtins.str:
        '''The Amazon Resource Name (ARN) of the resource to associate with the notification rule.

        Supported resources include pipelines in
        AWS CodePipeline, repositories in AWS CodeCommit, and build
        projects in AWS CodeBuild.
        '''
        result = self._values.get("resource")
        assert result is not None, "Required property 'resource' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NotificationRuleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@ithings/cdk-developer-tools-notifications.NotificationTargetProperty",
    jsii_struct_bases=[],
    name_mapping={"target_address": "targetAddress", "target_type": "targetType"},
)
class NotificationTargetProperty:
    def __init__(
        self,
        *,
        target_address: builtins.str,
        target_type: "TargetType",
    ) -> None:
        '''
        :param target_address: -
        :param target_type: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6b1d76f01146a0a147a570e07e8b247e9910249f36f77b14931c225033dda37)
            check_type(argname="argument target_address", value=target_address, expected_type=type_hints["target_address"])
            check_type(argname="argument target_type", value=target_type, expected_type=type_hints["target_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "target_address": target_address,
            "target_type": target_type,
        }

    @builtins.property
    def target_address(self) -> builtins.str:
        result = self._values.get("target_address")
        assert result is not None, "Required property 'target_address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_type(self) -> "TargetType":
        result = self._values.get("target_type")
        assert result is not None, "Required property 'target_type' is missing"
        return typing.cast("TargetType", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NotificationTargetProperty(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@ithings/cdk-developer-tools-notifications.PipelineEvent")
class PipelineEvent(enum.Enum):
    ACTION_EXECUTION_SUCCEEDED = "ACTION_EXECUTION_SUCCEEDED"
    ACTION_EXECUTION_FAILED = "ACTION_EXECUTION_FAILED"
    ACTION_EXECUTION_CANCELED = "ACTION_EXECUTION_CANCELED"
    ACTION_EXECUTION_STARTED = "ACTION_EXECUTION_STARTED"
    STAGE_EXECUTION_STARTED = "STAGE_EXECUTION_STARTED"
    STAGE_EXECUTION_SUCCEEDED = "STAGE_EXECUTION_SUCCEEDED"
    STAGE_EXECUTION_RESUMED = "STAGE_EXECUTION_RESUMED"
    STAGE_EXECUTION_CANCELED = "STAGE_EXECUTION_CANCELED"
    STAGE_EXECUTION_FAILED = "STAGE_EXECUTION_FAILED"
    PIPELINE_EXECUTION_FAILED = "PIPELINE_EXECUTION_FAILED"
    PIPELINE_EXECUTION_CANCELED = "PIPELINE_EXECUTION_CANCELED"
    PIPELINE_EXECUTION_STARTED = "PIPELINE_EXECUTION_STARTED"
    PIPELINE_EXECUTION_RESUMED = "PIPELINE_EXECUTION_RESUMED"
    PIPELINE_EXECUTION_SUCCEEDED = "PIPELINE_EXECUTION_SUCCEEDED"
    PIPELINE_EXECUTION_SUPERSEDED = "PIPELINE_EXECUTION_SUPERSEDED"
    MANUAL_APPROVAL_FAILED = "MANUAL_APPROVAL_FAILED"
    MANUAL_APPROVAL_NEEDED = "MANUAL_APPROVAL_NEEDED"
    MANUAL_APPROVAL_SUCCEEDED = "MANUAL_APPROVAL_SUCCEEDED"


class PipelineNotificationRule(
    NotificationRule,
    metaclass=jsii.JSIIMeta,
    jsii_type="@ithings/cdk-developer-tools-notifications.PipelineNotificationRule",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        events: typing.Sequence[PipelineEvent],
        pipeline: _aws_cdk_aws_codepipeline_ceddda9d.IPipeline,
        name: builtins.str,
        detail_type: typing.Optional[DetailType] = None,
        status: typing.Optional["Status"] = None,
        targets: typing.Optional[typing.Sequence[INotificationTarget]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param events: -
        :param pipeline: -
        :param name: The name for the notification rule. Notification rule names must be unique in your AWS account.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: FULL
        :param status: The status of the notification rule. The default value is ENABLED. If the status is set to DISABLED, notifications aren't sent for the notification rule. Default: ENABLED
        :param targets: SNS topics or AWS Chatbot clients to associate with the notification rule.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c43d76b3ee09f853d151db7beef8db2b1bec1b4dd83c0984f2f55d65aaf17ec3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = PipelineNotificationRuleProps(
            events=events,
            pipeline=pipeline,
            name=name,
            detail_type=detail_type,
            status=status,
            targets=targets,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@ithings/cdk-developer-tools-notifications.PipelineNotificationRuleProps",
    jsii_struct_bases=[CommonNotificationRuleProps],
    name_mapping={
        "name": "name",
        "detail_type": "detailType",
        "status": "status",
        "targets": "targets",
        "events": "events",
        "pipeline": "pipeline",
    },
)
class PipelineNotificationRuleProps(CommonNotificationRuleProps):
    def __init__(
        self,
        *,
        name: builtins.str,
        detail_type: typing.Optional[DetailType] = None,
        status: typing.Optional["Status"] = None,
        targets: typing.Optional[typing.Sequence[INotificationTarget]] = None,
        events: typing.Sequence[PipelineEvent],
        pipeline: _aws_cdk_aws_codepipeline_ceddda9d.IPipeline,
    ) -> None:
        '''
        :param name: The name for the notification rule. Notification rule names must be unique in your AWS account.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: FULL
        :param status: The status of the notification rule. The default value is ENABLED. If the status is set to DISABLED, notifications aren't sent for the notification rule. Default: ENABLED
        :param targets: SNS topics or AWS Chatbot clients to associate with the notification rule.
        :param events: -
        :param pipeline: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b7153410153169a8f358d199a5851d19d9fa7a94b682aaaffd37f1832ff5af6)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument detail_type", value=detail_type, expected_type=type_hints["detail_type"])
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
            check_type(argname="argument targets", value=targets, expected_type=type_hints["targets"])
            check_type(argname="argument events", value=events, expected_type=type_hints["events"])
            check_type(argname="argument pipeline", value=pipeline, expected_type=type_hints["pipeline"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "events": events,
            "pipeline": pipeline,
        }
        if detail_type is not None:
            self._values["detail_type"] = detail_type
        if status is not None:
            self._values["status"] = status
        if targets is not None:
            self._values["targets"] = targets

    @builtins.property
    def name(self) -> builtins.str:
        '''The name for the notification rule.

        Notification rule names
        must be unique in your AWS account.
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def detail_type(self) -> typing.Optional[DetailType]:
        '''The level of detail to include in the notifications for this resource.

        BASIC will include only the contents of the event
        as it would appear in AWS CloudWatch. FULL will include any
        supplemental information provided by AWS CodeStar Notifications
        and/or the service for the resource for which the notification
        is created.

        :default: FULL
        '''
        result = self._values.get("detail_type")
        return typing.cast(typing.Optional[DetailType], result)

    @builtins.property
    def status(self) -> typing.Optional["Status"]:
        '''The status of the notification rule.

        The default value is ENABLED.
        If the status is set to DISABLED, notifications aren't sent for
        the notification rule.

        :default: ENABLED
        '''
        result = self._values.get("status")
        return typing.cast(typing.Optional["Status"], result)

    @builtins.property
    def targets(self) -> typing.Optional[typing.List[INotificationTarget]]:
        '''SNS topics or AWS Chatbot clients to associate with the notification rule.'''
        result = self._values.get("targets")
        return typing.cast(typing.Optional[typing.List[INotificationTarget]], result)

    @builtins.property
    def events(self) -> typing.List[PipelineEvent]:
        result = self._values.get("events")
        assert result is not None, "Required property 'events' is missing"
        return typing.cast(typing.List[PipelineEvent], result)

    @builtins.property
    def pipeline(self) -> _aws_cdk_aws_codepipeline_ceddda9d.IPipeline:
        result = self._values.get("pipeline")
        assert result is not None, "Required property 'pipeline' is missing"
        return typing.cast(_aws_cdk_aws_codepipeline_ceddda9d.IPipeline, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineNotificationRuleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@ithings/cdk-developer-tools-notifications.ProjectEvent")
class ProjectEvent(enum.Enum):
    BUILD_STATE_FAILED = "BUILD_STATE_FAILED"
    BUILD_STATE_SUCCEEDED = "BUILD_STATE_SUCCEEDED"
    BUILD_STATE_IN_PROGRESS = "BUILD_STATE_IN_PROGRESS"
    BUILD_STATE_STOPPED = "BUILD_STATE_STOPPED"
    BUILD_PHASE_FAILURE = "BUILD_PHASE_FAILURE"
    BUILD_PHASE_SUCCESS = "BUILD_PHASE_SUCCESS"


class ProjectNotificationRule(
    NotificationRule,
    metaclass=jsii.JSIIMeta,
    jsii_type="@ithings/cdk-developer-tools-notifications.ProjectNotificationRule",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        events: typing.Sequence[ProjectEvent],
        project: _aws_cdk_aws_codebuild_ceddda9d.IProject,
        name: builtins.str,
        detail_type: typing.Optional[DetailType] = None,
        status: typing.Optional["Status"] = None,
        targets: typing.Optional[typing.Sequence[INotificationTarget]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param events: -
        :param project: -
        :param name: The name for the notification rule. Notification rule names must be unique in your AWS account.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: FULL
        :param status: The status of the notification rule. The default value is ENABLED. If the status is set to DISABLED, notifications aren't sent for the notification rule. Default: ENABLED
        :param targets: SNS topics or AWS Chatbot clients to associate with the notification rule.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b033f5813b32a19014ccf6d122d6b1f695f3ddbad65e6e6e3574b2c70fe3164b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ProjectNotificationRuleProps(
            events=events,
            project=project,
            name=name,
            detail_type=detail_type,
            status=status,
            targets=targets,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@ithings/cdk-developer-tools-notifications.ProjectNotificationRuleProps",
    jsii_struct_bases=[CommonNotificationRuleProps],
    name_mapping={
        "name": "name",
        "detail_type": "detailType",
        "status": "status",
        "targets": "targets",
        "events": "events",
        "project": "project",
    },
)
class ProjectNotificationRuleProps(CommonNotificationRuleProps):
    def __init__(
        self,
        *,
        name: builtins.str,
        detail_type: typing.Optional[DetailType] = None,
        status: typing.Optional["Status"] = None,
        targets: typing.Optional[typing.Sequence[INotificationTarget]] = None,
        events: typing.Sequence[ProjectEvent],
        project: _aws_cdk_aws_codebuild_ceddda9d.IProject,
    ) -> None:
        '''
        :param name: The name for the notification rule. Notification rule names must be unique in your AWS account.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: FULL
        :param status: The status of the notification rule. The default value is ENABLED. If the status is set to DISABLED, notifications aren't sent for the notification rule. Default: ENABLED
        :param targets: SNS topics or AWS Chatbot clients to associate with the notification rule.
        :param events: -
        :param project: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__871f84abc8954208010ee8b631b974c505c494e4cef01aa50fb73fbcec2db9ce)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument detail_type", value=detail_type, expected_type=type_hints["detail_type"])
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
            check_type(argname="argument targets", value=targets, expected_type=type_hints["targets"])
            check_type(argname="argument events", value=events, expected_type=type_hints["events"])
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "events": events,
            "project": project,
        }
        if detail_type is not None:
            self._values["detail_type"] = detail_type
        if status is not None:
            self._values["status"] = status
        if targets is not None:
            self._values["targets"] = targets

    @builtins.property
    def name(self) -> builtins.str:
        '''The name for the notification rule.

        Notification rule names
        must be unique in your AWS account.
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def detail_type(self) -> typing.Optional[DetailType]:
        '''The level of detail to include in the notifications for this resource.

        BASIC will include only the contents of the event
        as it would appear in AWS CloudWatch. FULL will include any
        supplemental information provided by AWS CodeStar Notifications
        and/or the service for the resource for which the notification
        is created.

        :default: FULL
        '''
        result = self._values.get("detail_type")
        return typing.cast(typing.Optional[DetailType], result)

    @builtins.property
    def status(self) -> typing.Optional["Status"]:
        '''The status of the notification rule.

        The default value is ENABLED.
        If the status is set to DISABLED, notifications aren't sent for
        the notification rule.

        :default: ENABLED
        '''
        result = self._values.get("status")
        return typing.cast(typing.Optional["Status"], result)

    @builtins.property
    def targets(self) -> typing.Optional[typing.List[INotificationTarget]]:
        '''SNS topics or AWS Chatbot clients to associate with the notification rule.'''
        result = self._values.get("targets")
        return typing.cast(typing.Optional[typing.List[INotificationTarget]], result)

    @builtins.property
    def events(self) -> typing.List[ProjectEvent]:
        result = self._values.get("events")
        assert result is not None, "Required property 'events' is missing"
        return typing.cast(typing.List[ProjectEvent], result)

    @builtins.property
    def project(self) -> _aws_cdk_aws_codebuild_ceddda9d.IProject:
        result = self._values.get("project")
        assert result is not None, "Required property 'project' is missing"
        return typing.cast(_aws_cdk_aws_codebuild_ceddda9d.IProject, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProjectNotificationRuleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@ithings/cdk-developer-tools-notifications.RepositoryEvent")
class RepositoryEvent(enum.Enum):
    COMMENTS_ON_COMMITS = "COMMENTS_ON_COMMITS"
    COMMENTS_ON_PULL_REQUEST = "COMMENTS_ON_PULL_REQUEST"
    APPROVAL_STATUS_CHANGED = "APPROVAL_STATUS_CHANGED"
    APPROVAL_RULE_OVERRIDE = "APPROVAL_RULE_OVERRIDE"
    PULL_REQUEST_CREATED = "PULL_REQUEST_CREATED"
    PULL_REQUEST_SOURCE_UPDATED = "PULL_REQUEST_SOURCE_UPDATED"
    PULL_REQUEST_STATUS_CHANGED = "PULL_REQUEST_STATUS_CHANGED"
    PULL_REQUEST_MERGED = "PULL_REQUEST_MERGED"
    BRANCHES_AND_TAGS_CREATED = "BRANCHES_AND_TAGS_CREATED"
    BRANCHES_AND_TAGS_DELETED = "BRANCHES_AND_TAGS_DELETED"
    BRANCHES_AND_TAGS_UPDATED = "BRANCHES_AND_TAGS_UPDATED"


class RepositoryNotificationRule(
    NotificationRule,
    metaclass=jsii.JSIIMeta,
    jsii_type="@ithings/cdk-developer-tools-notifications.RepositoryNotificationRule",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        events: typing.Sequence[RepositoryEvent],
        repository: _aws_cdk_aws_codecommit_ceddda9d.IRepository,
        name: builtins.str,
        detail_type: typing.Optional[DetailType] = None,
        status: typing.Optional["Status"] = None,
        targets: typing.Optional[typing.Sequence[INotificationTarget]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param events: -
        :param repository: -
        :param name: The name for the notification rule. Notification rule names must be unique in your AWS account.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: FULL
        :param status: The status of the notification rule. The default value is ENABLED. If the status is set to DISABLED, notifications aren't sent for the notification rule. Default: ENABLED
        :param targets: SNS topics or AWS Chatbot clients to associate with the notification rule.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d41b26849a15c8a894ef398d2c046ea747ae957ab99f7df9b05def007853923)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = RepositoryNotificationRuleProps(
            events=events,
            repository=repository,
            name=name,
            detail_type=detail_type,
            status=status,
            targets=targets,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@ithings/cdk-developer-tools-notifications.RepositoryNotificationRuleProps",
    jsii_struct_bases=[CommonNotificationRuleProps],
    name_mapping={
        "name": "name",
        "detail_type": "detailType",
        "status": "status",
        "targets": "targets",
        "events": "events",
        "repository": "repository",
    },
)
class RepositoryNotificationRuleProps(CommonNotificationRuleProps):
    def __init__(
        self,
        *,
        name: builtins.str,
        detail_type: typing.Optional[DetailType] = None,
        status: typing.Optional["Status"] = None,
        targets: typing.Optional[typing.Sequence[INotificationTarget]] = None,
        events: typing.Sequence[RepositoryEvent],
        repository: _aws_cdk_aws_codecommit_ceddda9d.IRepository,
    ) -> None:
        '''
        :param name: The name for the notification rule. Notification rule names must be unique in your AWS account.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: FULL
        :param status: The status of the notification rule. The default value is ENABLED. If the status is set to DISABLED, notifications aren't sent for the notification rule. Default: ENABLED
        :param targets: SNS topics or AWS Chatbot clients to associate with the notification rule.
        :param events: -
        :param repository: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30c93f40a7d57caf9e4f89dccc451e0f09d7f4b35c74ee554ca8dff9fde25c47)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument detail_type", value=detail_type, expected_type=type_hints["detail_type"])
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
            check_type(argname="argument targets", value=targets, expected_type=type_hints["targets"])
            check_type(argname="argument events", value=events, expected_type=type_hints["events"])
            check_type(argname="argument repository", value=repository, expected_type=type_hints["repository"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "events": events,
            "repository": repository,
        }
        if detail_type is not None:
            self._values["detail_type"] = detail_type
        if status is not None:
            self._values["status"] = status
        if targets is not None:
            self._values["targets"] = targets

    @builtins.property
    def name(self) -> builtins.str:
        '''The name for the notification rule.

        Notification rule names
        must be unique in your AWS account.
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def detail_type(self) -> typing.Optional[DetailType]:
        '''The level of detail to include in the notifications for this resource.

        BASIC will include only the contents of the event
        as it would appear in AWS CloudWatch. FULL will include any
        supplemental information provided by AWS CodeStar Notifications
        and/or the service for the resource for which the notification
        is created.

        :default: FULL
        '''
        result = self._values.get("detail_type")
        return typing.cast(typing.Optional[DetailType], result)

    @builtins.property
    def status(self) -> typing.Optional["Status"]:
        '''The status of the notification rule.

        The default value is ENABLED.
        If the status is set to DISABLED, notifications aren't sent for
        the notification rule.

        :default: ENABLED
        '''
        result = self._values.get("status")
        return typing.cast(typing.Optional["Status"], result)

    @builtins.property
    def targets(self) -> typing.Optional[typing.List[INotificationTarget]]:
        '''SNS topics or AWS Chatbot clients to associate with the notification rule.'''
        result = self._values.get("targets")
        return typing.cast(typing.Optional[typing.List[INotificationTarget]], result)

    @builtins.property
    def events(self) -> typing.List[RepositoryEvent]:
        result = self._values.get("events")
        assert result is not None, "Required property 'events' is missing"
        return typing.cast(typing.List[RepositoryEvent], result)

    @builtins.property
    def repository(self) -> _aws_cdk_aws_codecommit_ceddda9d.IRepository:
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(_aws_cdk_aws_codecommit_ceddda9d.IRepository, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RepositoryNotificationRuleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(INotificationTarget)
class SlackChannel(
    metaclass=jsii.JSIIMeta,
    jsii_type="@ithings/cdk-developer-tools-notifications.SlackChannel",
):
    def __init__(
        self,
        channel: _thpham_cdk_chatops_e462e3bd.ISlackChannelConfiguration,
    ) -> None:
        '''
        :param channel: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6515beeb8ddfc2b42f2d3e7eb85bd477c78ef6cc5c04e2e86f7e4891628d64a3)
            check_type(argname="argument channel", value=channel, expected_type=type_hints["channel"])
        jsii.create(self.__class__, self, [channel])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: _constructs_77d1e7e8.Construct,
        _rule: INotificationRule,
    ) -> NotificationTargetProperty:
        '''
        :param _scope: -
        :param _rule: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b762b44a827343c1f77ce967c36e46356d4c98bbb74b0f61b8e3471a9c454fe)
            check_type(argname="argument _scope", value=_scope, expected_type=type_hints["_scope"])
            check_type(argname="argument _rule", value=_rule, expected_type=type_hints["_rule"])
        return typing.cast(NotificationTargetProperty, jsii.invoke(self, "bind", [_scope, _rule]))


@jsii.implements(INotificationTarget)
class SnsTopic(
    metaclass=jsii.JSIIMeta,
    jsii_type="@ithings/cdk-developer-tools-notifications.SnsTopic",
):
    def __init__(self, topic: _aws_cdk_aws_sns_ceddda9d.ITopic) -> None:
        '''
        :param topic: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff0ecf7c6c98dcd1893c3db0e9eb66ec15282eafe884e5dce380f8ce0a765db6)
            check_type(argname="argument topic", value=topic, expected_type=type_hints["topic"])
        jsii.create(self.__class__, self, [topic])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: _constructs_77d1e7e8.Construct,
        _rule: INotificationRule,
    ) -> NotificationTargetProperty:
        '''
        :param _scope: -
        :param _rule: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c5c4ddad5268af005c973adf8deaffa62ea8cf1f577e75dfaca0d38c7937c9e)
            check_type(argname="argument _scope", value=_scope, expected_type=type_hints["_scope"])
            check_type(argname="argument _rule", value=_rule, expected_type=type_hints["_rule"])
        return typing.cast(NotificationTargetProperty, jsii.invoke(self, "bind", [_scope, _rule]))


@jsii.enum(jsii_type="@ithings/cdk-developer-tools-notifications.Status")
class Status(enum.Enum):
    DISABLED = "DISABLED"
    ENABLED = "ENABLED"


@jsii.enum(jsii_type="@ithings/cdk-developer-tools-notifications.TargetType")
class TargetType(enum.Enum):
    SNS = "SNS"
    AWS_CHATBOT_SLACK = "AWS_CHATBOT_SLACK"


class ApplicationNotificationRule(
    NotificationRule,
    metaclass=jsii.JSIIMeta,
    jsii_type="@ithings/cdk-developer-tools-notifications.ApplicationNotificationRule",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        application: typing.Union[_aws_cdk_aws_codedeploy_ceddda9d.IServerApplication, _aws_cdk_aws_codedeploy_ceddda9d.ILambdaApplication, _aws_cdk_aws_codedeploy_ceddda9d.IEcsApplication],
        events: typing.Sequence[ApplicationEvent],
        name: builtins.str,
        detail_type: typing.Optional[DetailType] = None,
        status: typing.Optional[Status] = None,
        targets: typing.Optional[typing.Sequence[INotificationTarget]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param application: -
        :param events: -
        :param name: The name for the notification rule. Notification rule names must be unique in your AWS account.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: FULL
        :param status: The status of the notification rule. The default value is ENABLED. If the status is set to DISABLED, notifications aren't sent for the notification rule. Default: ENABLED
        :param targets: SNS topics or AWS Chatbot clients to associate with the notification rule.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b72336781d9622ee1d2ae4c3dd78901bbf3c96f87548b4f4639b9407838335b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ApplicationNotificationRuleProps(
            application=application,
            events=events,
            name=name,
            detail_type=detail_type,
            status=status,
            targets=targets,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@ithings/cdk-developer-tools-notifications.ApplicationNotificationRuleProps",
    jsii_struct_bases=[CommonNotificationRuleProps],
    name_mapping={
        "name": "name",
        "detail_type": "detailType",
        "status": "status",
        "targets": "targets",
        "application": "application",
        "events": "events",
    },
)
class ApplicationNotificationRuleProps(CommonNotificationRuleProps):
    def __init__(
        self,
        *,
        name: builtins.str,
        detail_type: typing.Optional[DetailType] = None,
        status: typing.Optional[Status] = None,
        targets: typing.Optional[typing.Sequence[INotificationTarget]] = None,
        application: typing.Union[_aws_cdk_aws_codedeploy_ceddda9d.IServerApplication, _aws_cdk_aws_codedeploy_ceddda9d.ILambdaApplication, _aws_cdk_aws_codedeploy_ceddda9d.IEcsApplication],
        events: typing.Sequence[ApplicationEvent],
    ) -> None:
        '''
        :param name: The name for the notification rule. Notification rule names must be unique in your AWS account.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: FULL
        :param status: The status of the notification rule. The default value is ENABLED. If the status is set to DISABLED, notifications aren't sent for the notification rule. Default: ENABLED
        :param targets: SNS topics or AWS Chatbot clients to associate with the notification rule.
        :param application: -
        :param events: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0f88850e99af94c56906712b0e9b2e060fb7f5c139c44b4b1400ec659740d54)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument detail_type", value=detail_type, expected_type=type_hints["detail_type"])
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
            check_type(argname="argument targets", value=targets, expected_type=type_hints["targets"])
            check_type(argname="argument application", value=application, expected_type=type_hints["application"])
            check_type(argname="argument events", value=events, expected_type=type_hints["events"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "application": application,
            "events": events,
        }
        if detail_type is not None:
            self._values["detail_type"] = detail_type
        if status is not None:
            self._values["status"] = status
        if targets is not None:
            self._values["targets"] = targets

    @builtins.property
    def name(self) -> builtins.str:
        '''The name for the notification rule.

        Notification rule names
        must be unique in your AWS account.
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def detail_type(self) -> typing.Optional[DetailType]:
        '''The level of detail to include in the notifications for this resource.

        BASIC will include only the contents of the event
        as it would appear in AWS CloudWatch. FULL will include any
        supplemental information provided by AWS CodeStar Notifications
        and/or the service for the resource for which the notification
        is created.

        :default: FULL
        '''
        result = self._values.get("detail_type")
        return typing.cast(typing.Optional[DetailType], result)

    @builtins.property
    def status(self) -> typing.Optional[Status]:
        '''The status of the notification rule.

        The default value is ENABLED.
        If the status is set to DISABLED, notifications aren't sent for
        the notification rule.

        :default: ENABLED
        '''
        result = self._values.get("status")
        return typing.cast(typing.Optional[Status], result)

    @builtins.property
    def targets(self) -> typing.Optional[typing.List[INotificationTarget]]:
        '''SNS topics or AWS Chatbot clients to associate with the notification rule.'''
        result = self._values.get("targets")
        return typing.cast(typing.Optional[typing.List[INotificationTarget]], result)

    @builtins.property
    def application(
        self,
    ) -> typing.Union[_aws_cdk_aws_codedeploy_ceddda9d.IServerApplication, _aws_cdk_aws_codedeploy_ceddda9d.ILambdaApplication, _aws_cdk_aws_codedeploy_ceddda9d.IEcsApplication]:
        result = self._values.get("application")
        assert result is not None, "Required property 'application' is missing"
        return typing.cast(typing.Union[_aws_cdk_aws_codedeploy_ceddda9d.IServerApplication, _aws_cdk_aws_codedeploy_ceddda9d.ILambdaApplication, _aws_cdk_aws_codedeploy_ceddda9d.IEcsApplication], result)

    @builtins.property
    def events(self) -> typing.List[ApplicationEvent]:
        result = self._values.get("events")
        assert result is not None, "Required property 'events' is missing"
        return typing.cast(typing.List[ApplicationEvent], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApplicationNotificationRuleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ApplicationEvent",
    "ApplicationNotificationRule",
    "ApplicationNotificationRuleProps",
    "CommonNotificationRuleProps",
    "DetailType",
    "INotificationRule",
    "INotificationTarget",
    "MSTeamsIncomingWebhook",
    "NotificationRule",
    "NotificationRuleProps",
    "NotificationTargetProperty",
    "PipelineEvent",
    "PipelineNotificationRule",
    "PipelineNotificationRuleProps",
    "ProjectEvent",
    "ProjectNotificationRule",
    "ProjectNotificationRuleProps",
    "RepositoryEvent",
    "RepositoryNotificationRule",
    "RepositoryNotificationRuleProps",
    "SlackChannel",
    "SnsTopic",
    "Status",
    "TargetType",
]

publication.publish()

def _typecheckingstub__3a937243bd2bef97f731586167f55110a65585b66de15fefb6b51e3fea67e6fc(
    *,
    name: builtins.str,
    detail_type: typing.Optional[DetailType] = None,
    status: typing.Optional[Status] = None,
    targets: typing.Optional[typing.Sequence[INotificationTarget]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b541b2224cd7d8ca242f888c6ceab1812dfe9ca62b16fffb866f5ed2e8011e98(
    scope: _constructs_77d1e7e8.Construct,
    rule: INotificationRule,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__730bc001b37af829435fb7e9c7d533d5e64c2a9c689f8caac23c118946ff9260(
    webhook: _thpham_cdk_chatops_e462e3bd.MSTeamsIncomingWebhookConfiguration,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b831de9b8b1c3e926d3d65bf9b15eeca85dfd72ce9a5e92be24d3780bbb21d0(
    scope: _constructs_77d1e7e8.Construct,
    _rule: INotificationRule,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be764047800f4e67e91c73cea28b16a9d91598104b2e4f5bd4b840c4f0b9a1d5(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    events: typing.Sequence[typing.Union[RepositoryEvent, PipelineEvent, ProjectEvent, ApplicationEvent]],
    resource: builtins.str,
    name: builtins.str,
    detail_type: typing.Optional[DetailType] = None,
    status: typing.Optional[Status] = None,
    targets: typing.Optional[typing.Sequence[INotificationTarget]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67e7aaaf439297abc0f5d41fccb066e3a3979d67370d947d244889cfccd44876(
    target: INotificationTarget,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88462a85c912a642d612e9157fe1f4ad046391d9eaff76429454bca05a8c6fe8(
    *,
    name: builtins.str,
    detail_type: typing.Optional[DetailType] = None,
    status: typing.Optional[Status] = None,
    targets: typing.Optional[typing.Sequence[INotificationTarget]] = None,
    events: typing.Sequence[typing.Union[RepositoryEvent, PipelineEvent, ProjectEvent, ApplicationEvent]],
    resource: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6b1d76f01146a0a147a570e07e8b247e9910249f36f77b14931c225033dda37(
    *,
    target_address: builtins.str,
    target_type: TargetType,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c43d76b3ee09f853d151db7beef8db2b1bec1b4dd83c0984f2f55d65aaf17ec3(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    events: typing.Sequence[PipelineEvent],
    pipeline: _aws_cdk_aws_codepipeline_ceddda9d.IPipeline,
    name: builtins.str,
    detail_type: typing.Optional[DetailType] = None,
    status: typing.Optional[Status] = None,
    targets: typing.Optional[typing.Sequence[INotificationTarget]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b7153410153169a8f358d199a5851d19d9fa7a94b682aaaffd37f1832ff5af6(
    *,
    name: builtins.str,
    detail_type: typing.Optional[DetailType] = None,
    status: typing.Optional[Status] = None,
    targets: typing.Optional[typing.Sequence[INotificationTarget]] = None,
    events: typing.Sequence[PipelineEvent],
    pipeline: _aws_cdk_aws_codepipeline_ceddda9d.IPipeline,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b033f5813b32a19014ccf6d122d6b1f695f3ddbad65e6e6e3574b2c70fe3164b(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    events: typing.Sequence[ProjectEvent],
    project: _aws_cdk_aws_codebuild_ceddda9d.IProject,
    name: builtins.str,
    detail_type: typing.Optional[DetailType] = None,
    status: typing.Optional[Status] = None,
    targets: typing.Optional[typing.Sequence[INotificationTarget]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__871f84abc8954208010ee8b631b974c505c494e4cef01aa50fb73fbcec2db9ce(
    *,
    name: builtins.str,
    detail_type: typing.Optional[DetailType] = None,
    status: typing.Optional[Status] = None,
    targets: typing.Optional[typing.Sequence[INotificationTarget]] = None,
    events: typing.Sequence[ProjectEvent],
    project: _aws_cdk_aws_codebuild_ceddda9d.IProject,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d41b26849a15c8a894ef398d2c046ea747ae957ab99f7df9b05def007853923(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    events: typing.Sequence[RepositoryEvent],
    repository: _aws_cdk_aws_codecommit_ceddda9d.IRepository,
    name: builtins.str,
    detail_type: typing.Optional[DetailType] = None,
    status: typing.Optional[Status] = None,
    targets: typing.Optional[typing.Sequence[INotificationTarget]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30c93f40a7d57caf9e4f89dccc451e0f09d7f4b35c74ee554ca8dff9fde25c47(
    *,
    name: builtins.str,
    detail_type: typing.Optional[DetailType] = None,
    status: typing.Optional[Status] = None,
    targets: typing.Optional[typing.Sequence[INotificationTarget]] = None,
    events: typing.Sequence[RepositoryEvent],
    repository: _aws_cdk_aws_codecommit_ceddda9d.IRepository,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6515beeb8ddfc2b42f2d3e7eb85bd477c78ef6cc5c04e2e86f7e4891628d64a3(
    channel: _thpham_cdk_chatops_e462e3bd.ISlackChannelConfiguration,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b762b44a827343c1f77ce967c36e46356d4c98bbb74b0f61b8e3471a9c454fe(
    _scope: _constructs_77d1e7e8.Construct,
    _rule: INotificationRule,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff0ecf7c6c98dcd1893c3db0e9eb66ec15282eafe884e5dce380f8ce0a765db6(
    topic: _aws_cdk_aws_sns_ceddda9d.ITopic,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c5c4ddad5268af005c973adf8deaffa62ea8cf1f577e75dfaca0d38c7937c9e(
    _scope: _constructs_77d1e7e8.Construct,
    _rule: INotificationRule,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b72336781d9622ee1d2ae4c3dd78901bbf3c96f87548b4f4639b9407838335b(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    application: typing.Union[_aws_cdk_aws_codedeploy_ceddda9d.IServerApplication, _aws_cdk_aws_codedeploy_ceddda9d.ILambdaApplication, _aws_cdk_aws_codedeploy_ceddda9d.IEcsApplication],
    events: typing.Sequence[ApplicationEvent],
    name: builtins.str,
    detail_type: typing.Optional[DetailType] = None,
    status: typing.Optional[Status] = None,
    targets: typing.Optional[typing.Sequence[INotificationTarget]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0f88850e99af94c56906712b0e9b2e060fb7f5c139c44b4b1400ec659740d54(
    *,
    name: builtins.str,
    detail_type: typing.Optional[DetailType] = None,
    status: typing.Optional[Status] = None,
    targets: typing.Optional[typing.Sequence[INotificationTarget]] = None,
    application: typing.Union[_aws_cdk_aws_codedeploy_ceddda9d.IServerApplication, _aws_cdk_aws_codedeploy_ceddda9d.ILambdaApplication, _aws_cdk_aws_codedeploy_ceddda9d.IEcsApplication],
    events: typing.Sequence[ApplicationEvent],
) -> None:
    """Type checking stubs"""
    pass
